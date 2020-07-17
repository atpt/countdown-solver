from random import randrange, shuffle, choice
import operator
from copy import deepcopy

class Puzzle:
	targetMin=101
	targetMax=1000
	numbers=6
	bigNumbers=[25,50,75,100]
	smallNumbers=[i for i in range(1,10)] + [i for i in range(1,10)]

	def __init__(self, big, small):
		if((not isinstance(big, int)) or (not isinstance(small, int)) or ((big+small) != self.numbers) or (big > len(self.bigNumbers)) or (small > len(self.smallNumbers)) or (big < 0) or (small < 0)):
			raise Exception("Invalid arguments",big,small)
		self.target = randrange(self.targetMin, self.targetMax)
		shuffle(self.bigNumbers)
		shuffle(self.smallNumbers)
		self.numbers = self.smallNumbers[:small] + self.bigNumbers[:big]

	def getTarget(self):
		return self.target

	def getNumbers(self):
		return self.numbers

	def toString(self):
		return "Target: " + str(self.target) + "\nNumbers: " + ' '.join(map(str,self.numbers))

	def isSolution(self, expression):
		if(not isinstance(expression, Expression)):
			raise Exception("Invalid argument",expression)
		return expression.evaluate() == self.target

class Expression:
	pass

class BinaryExpression(Expression):
	reverseTable = {"+":"-", "-":"+", "*":"/", "/":"*"}
	def __init__(self, op, exp1, exp2):
		if((not isinstance(op, str)) or (not isinstance(exp1, Expression)) or (not isinstance(exp2, Expression))):
			raise Exception("Invalid arguments",op,exp1,exp2)
		self.opString = op
		self.op = self.stringToOperator(op)
		self.left = exp1
		self.right = exp2
		self.numbers = (self.left.getNumbers()) + (self.right.getNumbers())

	def setLeft(self, exp):
		if(not isinstance(exp, Expression)):
			raise Exception("Invalid argument",exp)
		self.left = exp
		self.numbers = (self.left.getNumbers()) + (self.right.getNumbers())

	def setRight(self, exp):
		if(not isinstance(exp, Expression)):
			raise Exception("Invalid argument",exp)
		self.right = exp
		self.numbers = (self.left.getNumbers()) + (self.right.getNumbers())

	def setOperator(self, op):
		if(not isinstance(exp, str)):
			raise Exception("Invalid argument",op)
		self.opString = op
		self.op = stringToOperator(op)

	def evaluate(self):
		try:
			value = self.op(self.left.evaluate(), self.right.evaluate())
		except ZeroDivisionError:
			return "illegal"
		if((value < 0) or (int(value) != value)):
			return "illegal"
		return value

	def toString(self):
		return "("+ self.left.toString() + self.opString + self.right.toString() + ")"

	def stringToOperator(self, string):
		if(string == "+"):
			return operator.add
		elif(string == "-"):
			return operator.sub
		elif(string == "*"):
			return operator.mul
		elif(string == "/"):
			return operator.truediv
		else:
			raise Exception("Invalid operator", op)

	def getNumbers(self):
		return self.numbers

	def size(self):
		return self.left.size() + self.right.size()

	# This is actually definition of isomorphism, not equivalence
	# def isEqual(self, exp):
	# 	if(not isinstance(exp, BinaryExpression)):
	# 		return False
	# 	return (self.opString == exp.opString) and ((self.left.isEqual(exp.left) and self.right.isEqual(exp.right)) or (self.left.isEqual(exp.right) and self.right.isEqual(exp.left)))

	def isEqual(self, exp):
		return (isinstance(exp, BinaryExpression)) and (self.getNumbers().sort() == exp.getNumbers().sort()) and (self.evaluate() == exp.evaluate())

	def isLegal(self):
		return self.left.isLegal() and self.right.isLegal() and (not self.evaluate() == "illegal")

	def reverseOp(self, string):
		return self.reverseTable[string]

	def merge(self, exp):
		print("Merging: "+self.toString()+" and "+exp.toString())
		if(isinstance(exp, PrimitiveExpression)):
			print("Finished with: "+self.toString())
			return self
		answerOnLeft = exp.answerOnLeft()
		if(answerOnLeft):
			newExp = BinaryExpression(self.reverseOp(exp.opString), self, exp.right)
			return newExp.merge(exp.left)
		else:
			newExp = BinaryExpression(self.reverseOp(exp.opString), exp.left, self)
			return newExp.merge(exp.right)

	def answerOnLeft(self):
		return self.left.answer()

	def answer(self):
		return (self.left.answer() or self.right.answer())

class PrimitiveExpression(Expression):
	reverseTable = {"+":"-", "-":"+", "*":"/", "/":"*"}

	def __init__(self, x):
		if(not isinstance(x, int)):
			raise Exception("Invalid argument",x)
		self.value = x
		self.numbers = [x]

	def evaluate(self):
		return self.value

	def reverseOp(self, string):
		return self.reverseTable[string]

	def setValue(self, v):
		if(not isinstance(v, int)):
			raise Exception("Invalid argument",v)
		self.value = v
		self.numbers = [v]

	def toString(self):
		return str(self.evaluate())

	def getNumbers(self):
		return self.numbers

	def answer(self):
		return (self.value > 100)

	def answerOnLeft(self):
		return (self.value > 100)

	def size(self):
		return 1

	def isEqual(self, exp):
		return isinstance(exp, PrimitiveExpression) and (self.value == exp.value)

	def isLegal(self):
		return True;

	def merge(self, exp):
		print("Merging: "+self.toString()+" and "+exp.toString())
		if(isinstance(exp, PrimitiveExpression)):
			print("Finished with: "+self.toString())
			return self
		answerOnLeft = exp.answerOnLeft()
		if(answerOnLeft):
			newExp = BinaryExpression(self.reverseOp(exp.opString), self, exp.right)
			return newExp.merge(exp.left)
		else:
			newExp = BinaryExpression(self.reverseOp(exp.opString), exp.left, self)
			return newExp.merge(exp.right)

class Solver:
	ops = ["+", "-", "*", "/"]

	def __init__(self, puzzle):
		if(not isinstance(puzzle, Puzzle)):
			raise Exception("Invalid argument",puzzle)
		self.puzzle = puzzle
		self.numbers = puzzle.getNumbers()
		self.target = puzzle.getTarget()
		self.freqDict = {}
		for n in self.numbers:
			if(n in self.freqDict):
				self.freqDict[n] += 1
			else:
				self.freqDict[n] = 1

	def numbersUnused(self, used):
		return [i for i in self.numbers if (i not in used)]

	# True if (equivalent to) exp is already in expList
	def alreadyGuessed(self, expList, exp):
		for e in expList:
			if(exp.isEqual(e)):
				return True
		return False

	def usesTooMany(self, used1, used2):
		dict = deepcopy(self.freqDict)
		for x in (used1 + used2):
			if(x <= 100):
				dict[x] -= 1
				if(dict[x] < 0):
					return True
		return False

	def canMakeValue(self, val, used, expList):
		for e in expList:
			if((e.evaluate == val) and (not conflict(e.numbersUsed(), used))):
				return e
		return False

	def heuristic(self, exp):
		return abs(self.target - exp.evaluate())

	def zeroHeuristic(self, exp):
		return abs(0 - exp.evaluate())

	def checkMeetup(self, expList1, expList2):
		for s1 in expList1:
			for s2 in expList2:
				if((s1.evaluate() == s2.evaluate()) and (not self.usesTooMany(s1.getNumbers(), s2.getNumbers()))):
					return s1.merge(s2)

	def findEqualNeighbours(self, expList, index):
		value = expList[index].evaluate()
		output = []
		low = index
		while(low>=0):
			low -= 1
			if(expList[low].evaluate() != value):
				break
		high = index
		while(high<len(expList)):
			high += 1
			if(expList[high].evaluate() != value):
				break
		return expList[min(low+1,index):max(index+1, high)]

	def binarySearchHelper(self, expList, exp, lower, pivot, upper):
		comp = expList[pivot].evaluate() - exp.evaluate()
		if(comp == 0):
			return self.findEqualNeighbours(expList, pivot)
		elif(upper - lower <= 1):
			return "fail"
		elif(comp > 0):
			# expList[pivot] too high, go to lower half
			upper = pivot - 1
			pivot = int((lower + upper) / 2)
			return self.binarySearchHelper(expList, exp, lower, pivot, upper)
		else:
			lower = pivot + 1
			pivot = int((lower + upper) / 2)
			return self.binarySearchHelper(expList, exp, lower, pivot, upper)


	def binarySearch(self, expList, exp):
		lower = 0
		pivot = int(len(expList) / 2)
		upper = len(expList) - 1
		return self.binarySearchHelper(expList, exp, lower, pivot, upper)

	def checkIndividualMeetup(self, expList, exp):
		sameValueExps = self.binarySearch(expList, exp)

		if(not isinstance(sameValueExps, str)):
			for e in sameValueExps:
				if(not self.usesTooMany(e.getNumbers(), exp.getNumbers())):
					return e.merge(exp)

	def solve(self):
		singlets = [PrimitiveExpression(n) for n in self.puzzle.getNumbers()]
		singlets.sort(key=lambda x: self.heuristic(x))
		if(self.heuristic(singlets[0]) == 0):
			return singlets[0]

		backSinglets = []
		targetExp = PrimitiveExpression(self.target)
		for op in self.ops:
			for s in singlets:
				exp = BinaryExpression(op, targetExp, s)
				if(exp.isLegal() and (not self.alreadyGuessed(backSinglets, exp))):
					backSinglets.append(exp)
				exp = BinaryExpression(op, s, targetExp)
				if(exp.isLegal() and (not self.alreadyGuessed(backSinglets, exp))):
					backSinglets.append(exp)
		backSinglets.sort(key=lambda x: self.zeroHeuristic(x))

		meet = self.checkMeetup(singlets, backSinglets)
		if(isinstance(meet, Expression)):
			return meet

		doublets = []
		for op in self.ops:
			for s1 in singlets:
				for s2 in singlets:
					if(not s1.isEqual(s2)):
						exp = BinaryExpression(op, s1, s2)
						if(exp.isLegal() and (not self.alreadyGuessed(doublets, exp))):
							doublets.append(exp)
						exp = BinaryExpression(op, s2, s1)
						if(exp.isLegal() and (not self.alreadyGuessed(doublets, exp))):
							doublets.append(exp)
		doublets.sort(key=lambda x: self.heuristic(x))
		if(self.heuristic(doublets[0]) == 0):
			return doublets[0]

		backDoublets = []
		for op in self.ops:
			for s1 in backSinglets:
				for s2 in singlets:
					if(not self.usesTooMany(s1.getNumbers(), s2.getNumbers())):
						exp = BinaryExpression(op, s1, s2)
						if(exp.isLegal() and (not self.alreadyGuessed(backDoublets, exp))):
							backDoublets.append(exp)
						exp = BinaryExpression(op, s2, s1)
						if(exp.isLegal() and (not self.alreadyGuessed(backDoublets, exp))):
							backDoublets.append(exp)
		backDoublets.sort(key=lambda x: self.zeroHeuristic(x))

		meet = self.checkMeetup(singlets+doublets, backSinglets+backDoublets)
		if(isinstance(meet, Expression)):
			return meet

		triplets = []
		for op in self.ops:
			for s1 in doublets:
				for s2 in singlets:
					if(not self.usesTooMany(s1.getNumbers(), s2.getNumbers())):
						exp = BinaryExpression(op, s1, s2)
						if(exp.isLegal() and (not self.alreadyGuessed(triplets, exp))):
							triplets.append(exp)
						exp = BinaryExpression(op, s2, s1)
						if(exp.isLegal() and (not self.alreadyGuessed(triplets, exp))):
							triplets.append(exp)
		triplets.sort(key=lambda x: self.heuristic(x))
		if(self.heuristic(triplets[0]) == 0):
			return triplets[0]

		forwardChains = singlets + doublets + triplets
		forwardChains.sort(key=lambda x: x.evaluate())

		iters = 0
		backTriplets = []
		for op in self.ops:
			for s1 in backDoublets:
				for s2 in singlets:
					iters+=1
					if(iters%1000==0):
						print(iters)
					if(not self.usesTooMany(s1.getNumbers(), s2.getNumbers())):
						exp = BinaryExpression(op, s1, s2)
						if(exp.isLegal() and (not self.alreadyGuessed(backTriplets, exp))):
							meet = self.checkIndividualMeetup(forwardChains, exp)
							if(isinstance(meet, Expression)):
								return meet
							backTriplets.append(exp)
						exp = BinaryExpression(op, s2, s1)
						if(exp.isLegal() and (not self.alreadyGuessed(backTriplets, exp))):
							meet = self.checkIndividualMeetup(forwardChains, exp)
							if(isinstance(meet, Expression)):
								return meet
							backTriplets.append(exp)
		backTriplets.sort(key=lambda x: self.zeroHeuristic(x))

		meet = self.checkMeetup(singlets+doublets+triplets, backSinglets+backDoublets+backTriplets)
		if(isinstance(meet, Expression)):
			return meet

		print("Closest: "+triplets[0].toString()+" = "+str(triplets[0].evaluate()))
		return PrimitiveExpression(-1)

def main():

	while(True):
		puzzle = Puzzle(2,4)
		print(puzzle.toString())

		solver = Solver(puzzle)
		solution = solver.solve().toString()
		print(solution)
		print("="+str(eval(solution)))

	# solution = solver.forwardChain()
	# if(isinstance(solution, str)):
	# 	print(solution)
	# else:
	# 	print(solution.toString())

	# while True:
	# 	bigs = randrange(0,5)
	# 	puzzle = Puzzle(bigs,6-bigs)
	# 	solver = Solver(puzzle)
	# 	solution = solver.forwardChain()
	# 	if(isinstance(solution, str)):
	# 		print(puzzle.toString())
	# 		print(solution)
	# 		break

	# exp1 = BinaryExpression("-", PrimitiveExpression(3), PrimitiveExpression(1))
	# exp2 = BinaryExpression("-", PrimitiveExpression(2), PrimitiveExpression(1))
	#
	# print(exp1.isEqual(exp2))

if __name__ == "__main__":
	main()
