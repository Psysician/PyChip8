
def get_int(n):
	return int(n.num if isinstance(n, Byte) else n)

class Byte:
	mask = 0xFF

	def __init__(self, number=None, wrapped=False):
		num = number
		if isinstance(number, Byte):
			num = number.num

		self.num = (int(num) & type(self).mask) if num else 0
		self.wrapped = wrapped or (num and self.num != num)


	def __add__(self, other):
		return type(self)(self.num + get_int(other))

	def __radd__(self, other):
		return self.__add__(other)

	def __iadd__(self, other):
		self.num += get_int(other)
		masked = self.num & type(self).mask
		self.wrapped = masked != self.num
		self.num &= masked
		return self


	def __sub__(self, other):
		return type(self)(self.num - get_int(other))

	def __rsub__(self, other):
		return type(self)((get_int(other)) - self.num)

	def __isub__(self, other):
		othernum = get_int(other)
		self.wrapped = self.num < othernum
		self.num -= othernum
		return self


	def __mul__(self, other):
		return type(self)(self.num * (get_int(other)))

	def __rmul__(self, other):
		return self.__mul__(other)

	def __imul__(self, other):
		self.num *= get_int(other)
		masked = self.num & type(self).mask
		self.wrapped = masked != self.num
		self.num &= masked
		return self


	def __truediv__(self, other):
		return type(self)(self.num // (get_int(other)))

	def __rtruediv__(self, other):
		return type(self)((get_int(other)) // self.num)

	def __itruediv__(self, other):
		self.num //= get_int(other)
		return self

	def __floordiv__(self, other):
		return self.__truediv__(other)

	def __rfloordiv__(self, other):
		return self.__rtruediv__(other)
	
	def __ifloordiv__(self, other):
		return self.__itruediv__(other)


	def __mod__(self, other):
		return type(self)(self.num % (get_int(other)))
	
	def __rmod__(self, other):
		return type(self)((get_int(other)) % self.num)

	def __imod__(self, other):
		self.num %= get_int(other)
		return self


	def __pow__(self, other, mod):
		return type(self)(self.num.__pow__((get_int(other)), mod))
	
	def __rpow__(self, other, mod):
		return type(self)(self.num.__rpow__((get_int(other)), mod))
	
	def __ipow__(self, other):
		self.num **= get_int(other)
		masked = self.num & type(self).mask
		self.wrapped = masked != self.num
		self.num &= masked
		return self


	def __lshift__(self, other):
		return type(self)(self.num << (get_int(other)))

	def __rlshift__(self, other):
		return type(self)((get_int(other)) << self.num)

	def __ilshift__(self, other):
		self.num <<= get_int(other)
		self.num &= type(self).mask
		return self

	
	def __rshift__(self, other):
		return type(self)(self.num >> (get_int(other)))

	def __rrshift__(self, other):
		return type(self)((get_int(other)) >> self.num)

	def __irshift__(self, other):
		self.num >>= get_int(other)
		self.num &= type(self).mask
		return self


	def __and__(self, other):
		return type(self)(self.num & (get_int(other)))

	def __rand__(self, other):
		return self.__and__(other)

	def __iand__(self, other):
		self.num &= get_int(other)
		self.num &= type(self).mask
		return self


	def __or__(self, other):
		return type(self)(self.num | (get_int(other)))

	def __ror__(self, other):
		return self.__or__(other)

	def __ior__(self, other):
		self.num |= get_int(other)
		self.num &= type(self).mask
		return self


	def __xor__(self, other):
		return type(self)(self.num ^ (get_int(other)))

	def __rxor__(self, other):
		return self.__xor__(other)

	def __ixor__(self, other):
		self.num ^= get_int(other)
		self.num &= type(self).mask
		return self


	def __neg__(self):
		return type(self)(-self.num)

	def __pos__(self):
		return type(self)(+self.num)

	def __abs__(self):
		return type(self)(self.num.__abs__())

	def __invert__(self):
		return type(self)(self.num.__invert__())


	def __lt__(self, other):
		return self.num.__lt__(get_int(other))

	def __le__(self, other):
		return self.num.__le__(get_int(other))
	
	def __gt__(self, other):
		return self.num.__gt__(get_int(other))

	def __ge__(self, other):
		return self.num.__ge__(get_int(other))

	def __eq__(self, other):
		return self.num.__eq__(get_int(other))
	def __ne__(self, other):
		return self.num.__ne__(get_int(other))


	def __int__(self):
		return self.num

	def __float__(self):
		return float(self.num)


	def __index__(self):
		return self.num

	def __str__(self):
		return "{:02X}".format(self.num)

	def __repr__(self):
		return "0x" + self.__str__()


class Short(Byte):
	mask = 0xFFFF

	@staticmethod
	def from_bytes(a: Byte, b: Byte):
		return Short((a.num << 8) | b.num)

	def __str__(self):
		return "{:04X}".format(self.num)


class TypedArray:
	def __init__(self, ty, val=None):
		self.ty = ty
		self.vals = []

		if not val is None:
			if type(val) is list:
				for v in val:
					self.append(v)
			else:
				self.append(val)

	def append(self, val):
		if type(val) == self.ty:
			self.vals.append(val)
		else:
			raise ValueError(f"{type(val)} != {self.ty}")

	def __getitem__(self, key):
		return self.vals.__getitem__(key)

	def __setitem__(self, key, val):
		if type(val) == self.ty:
			self.vals.__setitem__(key, val)
		else:
			raise ValueError(f"{type(val)} != {self.ty}")


def test():
	# overflow
	x = Byte(0xFF) + 1
	assert x == 0
	assert x.wrapped == True

	assert Short(0xFFFF) + 1 == 0

	x += 1
	assert x == 1
	assert x.wrapped == False # wrapped is reset


	# underflow
	x = Byte(0) - 1
	assert x == 0xFF
	assert x.wrapped == True

	assert Short(0) - 1 == 0xFFFF


	# shifting out of bounds
	assert Byte(1) << 8 == 0
	x = Byte(1)
	x <<= 8
	assert x == 0

	assert Short(1) << 8 == 0x100
	assert Short(1) << 16 == 0

	exit()

#test()
