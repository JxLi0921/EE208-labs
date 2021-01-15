class Highlighter:
	def __init__(self, keys: list, 
	             pre_tag:  str=' <em><font style=\"color:red;\"> ', 
				 post_tag: str=' </font></em>') -> None:
		'''
			Initialize a highlighter.
			Input:
				keys: a list, the keywords of the highlighter.
				pre_tag: a str, the HTML pre tag of the highlighter.
				post_tag: a str, the HTML post tag of the highlighter.
			Return:
				None.
		'''
		self.keys = list(set(keys))
		self.pre_tag = pre_tag
		self.post_tag = post_tag

	def add_key(self, new_key: str) -> None:
		'''
			Add a new key to the highlighter if not exists.
		'''
		if new_key not in self.keys:
			self.keys.append(new_key)

	def get_keys(self) -> list:
		'''
			get the keys of the highlighter.
		'''
		return self.keys


	def highlight(self, s: str) -> str:
		'''
			Using the keywords of the highlighter to highlight the given str s,
			return the highlighted string.
		'''
		if not s:
			return ''
		for keyword in self.keys:
			s = s.replace(keyword, self.pre_tag + keyword + self.post_tag)

		return s

if __name__ == '__main__':
	# for test only.

	highlighter = Highlighter(['李政道', '物理'])
	res = highlighter.highlight('李政道研究所举办第3期李政道前沿讲坛暨Tsutomu,Yanagida教授聘任仪式')
	print(res)