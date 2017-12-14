from utilities import rom


def cb(data):
	# ``data`` can act as an object or dictionary. This function could have
	# actually just read::
	#     return data
	# ... but we will be explicit in what we return... yes this works!
	return {'lon': data.get('lon', 0), 'lat': data.get('lat', 0)}


class User(rom.Model):
	oid = rom.PrimaryKey()
	id = rom.String(required=True, unique=True, index=True, keygen=rom.IDENTITY_CI)
	name = rom.String()
	age = rom.Integer()

	def _before_insert(self):
		self._before_update()

	def _before_update(self):
		if self.talk_with is not None:
			self.is_talking = True
		else:
			self.is_talking = False

	talk_with = rom.OneToOne('User', 'no action')
	is_talking = rom.Boolean(index=True, default=False)
	lon = rom.Float(default=0)
	lat = rom.Float(default=0)
	geo_index = [
		# callback function passed to GeoIndex as the 2nd argument *must*
		# return a dictionary containing 'lon' and 'lat' values, as degrees
		rom.GeoIndex('geo_index', cb),
	]


if __name__ == '__main__':



	#user_1 = User(id=str(1), name="Utente a", age=12)
	#user_1.save()

	user_1 = User.get_by(id=str(1))
	print user_1

	user_2 = User.get_by(id=str(2))
	#user_2.talk_with = None
	#user_2.save()
	print user_2.talk_with.id

	#user_2 = User(id=str(2), name="Utente b", age=13)
	#user_2.save()



# users = User.get_by(uid=str(1))
# for user in users:
#	user.delete()
