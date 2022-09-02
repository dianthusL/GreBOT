class Town():
	def __init__(self):
		self.name = ""
		self.wood = ""
		self.stone = ""
		self.iron = ""
		self.population = ""
		self.max_storage = ""
		self.village_list = []
		
	def state(self):
		print("Nazwa wioski:", self.name
			,"; Drewno: ", self.wood
			,"; Kamien: ", self.stone
			,"; Srebro: ", self.iron
			,"; Populacja: ", self.population
			,"; Magazyn: ", self.max_storage
			)

class Village():
	def __init__(self):
		self.id =""
		

