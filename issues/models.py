from django.db import models

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
