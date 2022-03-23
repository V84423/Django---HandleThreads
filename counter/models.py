from django.db import models


class User(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=255)
	email = models.CharField(max_length=255)
	password = models.CharField(max_length=255)
	token = models.CharField(max_length=255)
	verfied = models.IntegerField(default=0)
	state = models.IntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'user'
	def __str__(self):
		return str(self.id)


class Shop(models.Model):
	id = models.AutoField(primary_key=True)
	url = models.TextField()
	shop = models.CharField(max_length=255)
	pachinko_rate = models.CharField(max_length=255)
	slot_rate = models.CharField(max_length=255)
	
	created_by_id = models.IntegerField(max_length=10)
	created_at = models.DateTimeField(auto_now_add=True)
	status = models.IntegerField(default=0)
	class Meta:
		db_table = 'shop'
	def __str__(self):
		return str(self.id)

class Machine(models.Model):
	id = models.AutoField(primary_key=True)
	url = models.TextField()
	shop = models.CharField(max_length=255)
	machine = models.CharField(max_length=255)
	ps = models.CharField(max_length=255)

	shop_id = models.IntegerField(max_length=10)
	created_by_id = models.IntegerField(max_length=10)
	created_at = models.DateTimeField(auto_now_add=True)
	status = models.IntegerField(default=0)
	class Meta:
		db_table = 'machine'
	def __str__(self):
		return str(self.id)

class Unit(models.Model):
	id = models.AutoField(primary_key=True)
	url = models.TextField()
	shop = models.CharField(max_length=255)
	machine = models.CharField(max_length=255)
	unit = models.CharField(max_length=255)
	ps = models.CharField(max_length=255)

	shop_id = models.IntegerField(max_length=10)
	machine_id = models.IntegerField(max_length=10)
	created_by_id = models.IntegerField(max_length=10)
	created_at = models.DateTimeField(auto_now_add=True)
	status = models.IntegerField(default=0)
	class Meta:
		db_table = 'unit'
	def __str__(self):
		return str(self.id)		


class Pachinko(models.Model):
	id = models.AutoField(primary_key=True)
	url = models.TextField()
	shop = models.CharField(max_length=255)
	machine = models.CharField(max_length=255)
	unit = models.CharField(max_length=255)

	most_bonus = models.CharField(max_length=255)
	probability = models.CharField(max_length=255)
	cumulative_start = models.CharField(max_length=255)
	yesterday_start = models.CharField(max_length=255)
	last_value = models.CharField(max_length=255)

	table = models.TextField()
	graph = models.TextField()

	shop_id = models.IntegerField(max_length=10) ############################ shop id - reference key
	machine_id = models.IntegerField(max_length=10) ############################ machine id - reference key
	unit_id = models.IntegerField(max_length=10) ############################ unit id - reference key
	created_by_id = models.IntegerField(max_length=10)
	created_at = models.DateField(auto_now_add=True)
	status = models.IntegerField(default=0)
	class Meta:
		db_table = 'pachinko'
	def __str__(self):
		return str(self.id)

class Slot(models.Model):
	id = models.AutoField(primary_key=True)
	url = models.TextField()
	shop = models.CharField(max_length=255)
	machine = models.CharField(max_length=255)
	unit = models.CharField(max_length=255)

	most_bonus = models.CharField(max_length=255)
	probability = models.CharField(max_length=255)
	BB_probability = models.CharField(max_length=255)
	RB_probability = models.CharField(max_length=255)
	cumulative_start = models.CharField(max_length=255)	
	yesterday_start = models.CharField(max_length=255)
	last_value = models.CharField(max_length=255)

	table = models.TextField()
	graph = models.TextField()

	shop_id = models.IntegerField(max_length=10) ############################ shop id - reference key
	machine_id = models.IntegerField(max_length=10) ############################ machine id - reference key
	unit_id = models.IntegerField(max_length=10) ############################ unit id - reference key
	created_by_id = models.IntegerField(max_length=10)
	created_at = models.DateField(auto_now_add=True)
	status = models.IntegerField(default=0)
	class Meta:
		db_table = 'slot'
	def __str__(self):
		return str(self.id)				

class Data(models.Model):
	id = models.AutoField(primary_key=True)
	url = models.TextField()
	shop = models.CharField(max_length=255)
	machine = models.CharField(max_length=255)
	unit = models.CharField(max_length=255)
	ps = models.CharField(max_length=255)

	most_bonus = models.CharField(max_length=255)
	probability = models.CharField(max_length=255)
	BB_probability = models.CharField(max_length=255)
	RB_probability = models.CharField(max_length=255)
	cumulative_start = models.CharField(max_length=255)	
	yesterday_start = models.CharField(max_length=255)
	last_value = models.CharField(max_length=255)

	table = models.TextField()
	graph = models.TextField()

	shop_id = models.IntegerField(max_length=10) ############################ shop id - reference key
	machine_id = models.IntegerField(max_length=10) ############################ machine id - reference key
	unit_id = models.IntegerField(max_length=10) ############################ unit id - reference key
	created_by_id = models.IntegerField(max_length=10)
	created_at = models.DateField(auto_now_add=True)
	status = models.IntegerField(default=0)
	class Meta:
		db_table = 'data'
	def __str__(self):
		return str(self.id)	
