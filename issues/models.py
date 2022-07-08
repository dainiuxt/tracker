from django.db import models
from authuser.models import User
from django.conf import settings
from datetime import date

class SoftDeleteQuerySet(models.QuerySet):
  def delete(self):
    self.update(deleted=True)

class SoftDeleteManager(models.Manager):
  use_for_related_fields = True

  def only_active(self):
    return self.all().exclude(deleted=True)

  def deleted(self):
    return self.only_active().filter(deleted=True)

  def get_queryset(self):
    return SoftDeleteQuerySet(self.model, using=self._db)


class SoftDeleteModel(models.Model):
  """ 
  Sets `deleted` state of model instead of deleting it
  """
  deleted = models.BooleanField(editable=False, default=False)  # NullBooleanField for faster migrations with Postgres if changing existing models
  class Meta:
    abstract = True

  def delete(self):
    self.deleted = True
    self.save()

  def restore(self):
    self.deleted = False
    self.save()

  objects = SoftDeleteManager()

# Employee.objects.all()           # will only return all, including deleted
# Employee.objects.only_active()   # gives you only NOT deleted
# Employee.objects.deleted()       # gives you only deleted objects

class Project(SoftDeleteModel):
  project_name = models.CharField('Project name', max_length=200)
  start_date = models.DateField('Start date')
  target_end = models.DateField('Target end date')
  actual_end = models.DateField('Actual end date', null=True, blank=True)
  created_on = models.DateField('Creation date', auto_now_add=True)
  created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT)
  assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='project_owner')
  # history = HistoricalRecords()

  def __str__(self):
    return self.project_name

  def pr_issues(self):
    issues = Issue.objects.filter(related_project=self.id)
    return issues

  def unresolved_issues(self):
    issues = Issue.objects.filter(related_project=self.id).filter(actual_resolution=None)
    return issues 
 

class Profile(SoftDeleteModel):
  user = models.OneToOneField(User, on_delete=models.PROTECT, blank=True)

  def __str__(self):
    return self.user.username

  class Meta:
    verbose_name = 'Person'
    verbose_name_plural = 'People'

  def show_deleted(self):
    return self.objects.deleted()

class Issue(SoftDeleteModel):
  summary = models.CharField('Issue summary', max_length=255)
  description = models.TextField('Description', null=True)
  identified_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, related_name='troubleshooter')
  identification_date = models.DateField('Identified on', auto_now_add=True)
  related_project = models.ForeignKey(Project, on_delete=models.PROTECT, null=True)
  assigned_to = models.ForeignKey(User, on_delete=models.PROTECT, null=True, related_name='issue_solver', blank=True)

  PIORITY_LIST = (
    ('l', 'Low'),
    ('m', 'Medium'),
    ('h', 'High'),
    ('e', 'Extra'),
  )

  priority = models.CharField('Priority', default='m', max_length=1, choices=PIORITY_LIST)
  target_resolution = models.DateField('Planned resolution')
  progress = models.TextField('Progress', null=True)
  actual_resolution = models.DateField('Actual resolution', null=True, blank=True)
  res_summary = models.TextField('Resolution summary', null=True, blank=True)
  created_on = models.DateField('Creation date', auto_now_add=True)
  created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name='creator')
  # history = HistoricalRecords()

  def resolved(self):
    if self.actual_resolution is None:
      return False
    else:
      return True

  def overdue(self):
    if self.actual_resolution is None and self.target_resolution < date.today():
      return True

  def __str__(self):
    return f"{self.summary}"
