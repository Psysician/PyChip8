
class Byte:
	def __init__(self, num=None):
		self.num = (int(num) & 0xFF) if num else 0

	def __add__(self, other):
		return type(self)(self.num + (other.num if type(other) is type(self) else other))

	def __radd__(self, other):
		return self.__add__(other)

	def __iadd__(self, other):
		self.num += other.num if type(other) is type(self) else other
		return self


	def __sub__(self, other):
		return type(self)(self.num - (other.num if type(other) is type(self) else other))

	def __rsub__(self, other):
		return type(self)((other.num if type(other) is type(self) else other) - self.num)

	def __isub__(self, other):
		self.num -= other.num if type(other) is type(self) else other
		return self


	def __mul__(self, other):
		return type(self)(self.num * (other.num if type(other) is type(self) else other))

	def __rmul__(self, other):
		return self.__mul__(other)

	def __imul__(self, other):
		self.num *= other.num if type(other) is type(self) else other
		return self


	def __truediv__(self, other):
		return type(self)(self.num // (other.num if type(other) is type(self) else other))

	def __rtruediv__(self, other):
		return type(self)((other.num if type(other) is type(self) else other) // self.num)

	def __itruediv__(self, other):
		self.num //= other.num if type(other) is type(self) else other
		return self

	def __floordiv__(self, other):
		return self.__truediv__(other)

	def __rfloordiv__(self, other):
		return self.__rtruediv__(other)
	
	def __ifloordiv__(self, other):
		return self.__itruediv__(other)


	def __mod__(self, other):
		return type(self)(self.num % (other.num if type(other) is type(self) else other))
	
	def __rmod__(self, other):
		return type(self)((other.num if type(other) is type(self) else other) % self.num)

	def __imod__(self, other):
		self.num %= other.num if type(other) is type(self) else other
		return self


	def __pow__(self, other, mod):
		return type(self)(self.num.__pow__((other.num if type(other) is type(self) else other), mod))
	
	def __rpow__(self, other, mod):
		return type(self)(self.num.__rpow__((other.num if type(other) is type(self) else other), mod))
	
	def __ipow__(self, other):
		self.num **= other.num if type(other) is type(self) else other
		return self


	def __lshift__(self, other):
		return type(self)(self.num << (other.num if type(other) is type(self) else other))

	def __rlshift__(self, other):
		return type(self)((other.num if type(other) is type(self) else other) << self.num)

	def __ilshift__(self, other):
		self.num <<= other.num if type(other) is type(self) else other
		return self

	
	def __rshift__(self, other):
		return type(self)(self.num >> (other.num if type(other) is type(self) else other))

	def __rrshift__(self, other):
		return type(self)((other.num if type(other) is type(self) else other) >> self.num)

	def __irshift__(self, other):
		self.num >>= other.num if type(other) is type(self) else other
		return self


	def __and__(self, other):
		return type(self)(self.num & (other.num if type(other) is type(self) else other))

	def __rand__(self, other):
		return self.__and__(other)

	def __iand__(self, other):
		self.num &= other.num if type(other) is type(self) else other
		return self


	def __or__(self, other):
		return type(self)(self.num | (other.num if type(other) is type(self) else other))

	def __ror__(self, other):
		return self.__or__(other)

	def __ior__(self, other):
		self.num |= other.num if type(other) is type(self) else other
		return self


	def __xor__(self, other):
		return type(self)(self.num ^ (other.num if type(other) is type(self) else other))

	def __xor__(self, other):
		return self.__xor__(other)

	def __ixor__(self, other):
		self.num ^= other.num if type(other) is type(self) else other
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
		return self.num.__lt__(other.num if type(other) is type(self) else other)

	def __le__(self, other):
		return self.num.__le__(other.num if type(other) is type(self) else other)
	
	def __gt__(self, other):
		return self.num.__gt__(other.num if type(other) is type(self) else other)

	def __ge__(self, other):
		return self.num.__ge__(other.num if type(other) is type(self) else other)

	def __eq__(self, other):
		return self.num.__eq__(other.num if type(other) is type(self) else other)
	def __ne__(self, other):
		return self.num.__ne__(other.num if type(other) is type(self) else other)


	def __int__(self):
		return self.num

	def __float__(self):
		return float(self.num)


	def __index__(self):
		return self.num

	def __str__(self):
		return hex(self.num)

	def __repr__(self):
		return hex(self.num)


class Short(Byte):
	def __init__(self, num=None):
		self.num = (int(num) & 0xFFFF) if num else 0

	def from_bytes(a: Byte, b: Byte):
		return Short((a.num << 8) | b.num)
