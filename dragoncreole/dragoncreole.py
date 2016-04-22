#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This file is part of DragonCreole
Copyright (C) 2013 - 2016 Zauber Paracelsus

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
'''

'''
==ABOUT==
DragonCreole is designed as a lightweight markup language, derived from
the Creole markup language (http://wikicreole.org/).  It includes an
expanded syntax and is optimized for high performance.
'''

try:
	from html import escape as escape
except:
	from cgi import escape as escape


import shlex, inspect, re, html2text, time, datetime

from types import *

regex_list = re.compile(r'\*+\s.+|\#+\s.+|\@+\s.+|\!+\s.+')
regex_list2 = re.compile(r'(\*+|\#+|\@+|\!+)')
regex_indent = re.compile(r'(\:+)')
rematch = re.match

class MacroObject():
	'''
		This class is used by macro functions to provide data about the page and a reference to the renderer
	'''
	__slots__ = ("body", "renderer")
	def __init__(self, body="", renderer=None):
		if(body != ""):
			if(body[0] == "\n"): body = body[1:]
		self.body = body
		self.renderer = renderer


class DragonCreole():
	"""
		The main renderer class.
	"""
	__slots__ = ("noMacros", "auto_paragraphs", "link_path", "image_path", "bodied_macros", "non_bodied_macros", "link_path_func", "link_class_func", "out_link_mark")
	def __init__(self, link_path="/", image_path="", bodied_macros={}, non_bodied_macros={}, link_path_func=None, link_class_func=None, out_link_mark = "➚", auto_paragraphs=True, noMacros=False):
		"""
			Returns a DragonCreole parser object.  The following optional arguments may be passed when creating a DragonCreole parser, in order to extend it.
			* link_path: The base path for all wiki links, which will be prepended to them.
			* image_path: The base path for all wiki images, which will be preprended to them.
			* bodied_macros: A dictionary of function references, which are called when the parser encounters a bodied macro.
			* non_bodied_macros: A dictionary of function references, which are called when the parser encounters a non-bodied macro.
			* link_path_func: A function reference which will be called to inspect any wiki link, and may modify its path.
			* link_class_func: A function reference which will be called to inspect any wiki link, and may modify its CSS class.
			* out_link_mark: A character which is appended to external links.  Set to a blank string for no mark.  Can be set to DragonCreole code, if desired, such as when one wishes to use an image or special formatting for the mark.
			* auto_paragraphs: If True, then paragraphs will automatically be created.
			* noMacros: If true, then macros will not be run.
		"""
		
		'''
		assert type(link_path) is str
		assert type(image_path) is str
		
		assert type(bodied_macros) is dict
		for func in bodied_macros:
			assert type(func) is FunctionType
		
		assert type(non_bodied_macros) is dict
		for func in non_bodied_macros:
			assert type(func) is FunctionType
		
		if(link_path_func != None):
			assert type(link_path_func) is FunctionType
		if(link_class_func != None):
			assert type(link_class_func) is FunctionType
		'''
		
		
		self.bodied_macros = {
			"block": self.macro_block
		}
		self.bodied_macros.update(bodied_macros)
		
		self.non_bodied_macros = {
			"datetime": self.macro_datetime
		}
		self.non_bodied_macros.update(non_bodied_macros)
		
		self.link_path = link_path
		self.image_path = image_path
		self.link_path_func = link_path_func
		self.link_class_func = link_class_func
		self.auto_paragraphs = auto_paragraphs
		self.noMacros = noMacros
		if(out_link_mark != ""):
			self.out_link_mark = self.process(out_link_mark)
		else:
			self.out_link_mark = out_link_mark
		return
	__cinit__ = __init__
	
	'''
	Renders a page to HTML
	'''
	def render(self, text, noMacros=None):
		return "\n".join(self.renderSub(text, noMacros))
		
	def renderSub(self, text, noMacros=None):
		frags = [x.strip() for x in text.split("\n")]
		if(frags == [""]):
			yield ""
			return
		i = -1
		skip = -1
		process = self.process
		for i, frag in enumerate(frags):
			if(skip > i):
				continue
			nextFrag = ""
			if(i+1 < len(frags)):
				nextFrag = frags[i+1]
			
			if(frag == ""):
				yield "\n"
			elif(frag[:1] == "="):
				yield self.handleHeading(frag)
			elif(frag[:2] == "\\\\"):
				yield "<br>"
			elif(frag[:4] == "----"):
				yield "<hr>"
			elif(frag[:1] in ">:"):
				yield self.handleParagraph(frag)
			elif(frag[:1] == "|"):
				if(i+1 < len(frags)):
					i2 = i+1
					while(i2 < len(frags)):
						if(frags[i2][:1] == "|"):
							frag += "\n" + frags[i2]
							i2 += 1
							skip = i2
						else:
							break
				yield self.handleTables(frag)
			elif(frag.startswith("{{{")):
				if(frag.endswith("}}}")):
					yield "<pre>{0}</pre>".format(frag[3:-3])
					continue
				nfrag = [frag]
				closed = False
				skip = i+1
				for ix, f in enumerate(frags[i+1:]):
					skip += 1
					nfrag += [f]
					if(f.endswith("}}}")):
						closed = True
						break
				if not closed:
					yield "<pre>{0}</pre>".format(escape("\n".join(nfrag)[3:]))
				else:
					yield "<pre>{0}</pre>".format(escape("\n".join(nfrag)[3:-3]))
			elif(frag.startswith("<<")):
				i2 = frag.find(">>")
				if(i2 != -1):
					macro = frag[2:i2].split(" ",1)[0]
					if(macro in self.bodied_macros):
						if(frag.endswith("<</"+macro+">>")):
							yield self.handleMacro(frag)[0]
							continue
						else:
							nfrag = [frag]
							closed = False
							skip = i+1
							for ix, f in enumerate(frags[i+1:]):
								skip += 1
								nfrag += [f]
								if(f.endswith("<</"+macro+">>")):
									closed = True
									break
							if not closed:
								nfrag += "<</"+macro+">>"
							yield self.handleMacro("\n".join(nfrag))[0]
							continue
				if(self.auto_paragraphs):
					yield "<p>" + process(frag) + "</p>"
				else:
					yield process(frag)
			elif(rematch(regex_list,frag) != None):
				if(i+1 < len(frags)):
					i2 = i+1
					while(i2 < len(frags)):
						if(rematch(regex_list,frags[i2]) != None):
							frag += "\n" + frags[i2]
							i2 += 1
							skip = i2
						else:
							break
				yield self.handleLists(frag)
			elif(frag[:1] == ";" and nextFrag[:1] == ":"):
				if(i+1 < len(frags)):
					frag += "\n" + nextFrag
					i += 2
					i2 = i
					while(i2 < len(frags)):
						if(frags[i2][:1] == ";" and frags[i2+1][:1] == ":"):
							frag += "\n" + frags[i2] + "\n" + frags[i2+1]
							i2 += 2
							skip = i2
						else:
							break
				yield self.handleDefinitionLists(frag)
			else:
				if(frag != ""):
					if(self.auto_paragraphs):
						yield "<p>" + process(frag) + "</p>"
					else:
						yield process(frag)
	
	def process(self, text, noMacros=None):
		if(noMacros!=None and type(noMacros) is bool):
			self.noMacros = noMacros
		skip = 0
		output=""
		length = len(text)-1
		blockStart=-1
		prevChar=""
		nextChar=""
		for i, c in enumerate(text):
			if(skip > 0):
				skip -= 1
				continue
			if(blockStart==-1):
				blockStart = i
			if(c in "~*/_^,-[{<\\"):
				if(i>0): prevChar = text[i-1]
				else: prevChar = ""
				if(i < length): nextChar = text[i+1]
				else: nextChar = ""
				
				body = ("",0)
				
				
				if(c in "~"):
					body = (nextChar,1)
				
				if(c[i:i+3] == "{{{"):
					body = self.handlePreformat(text[i:])
				elif(c in nextChar):
					if(c in "*/_^,-"):
						body = self.formatTag(text[i:], c, {
							"*":"b",
							"/":"i",
							"_":"u",
							"^":"sup",
							",":"sub",
							"-":"del"
						}[c])
					elif(c in "\\"):
						body = ("<br>",1)
					elif(c in "["):
						body = self.handleLink(text[i:])
					elif(c in "{"):
						body = self.handleImage(text[i:])
					elif(c in "<"):
						body = self.handleMacro(text[i:])
				
				if(body[0] != ""):
					if(blockStart != -1):
						output += escape(text[blockStart:i],True)
						blockStart=-1
					if(body[0] != ""):
						output += body[0]
					skip = body[1]
					continue
			if(i==length and blockStart != -1):
				output += escape(text[blockStart:])
		return output
	__call__=render
	
	'''
	Renders a page to a plain text form
	'''
	def plaintext(self, text):
		noMacros = self.noMacros
		toPlaintext = html2text.HTML2Text()
		toPlaintext.ignore_links = True
		ret = toPlaintext.handle(self.process(text, noMacros=True))
		self.noMacros = noMacros
		return ret
	
	'''
	Handles formatting for bold, italic, underlined, superscript, and subscript text
	'''
	def formatTag(self, text, mark, tag):
		temp = text[2:].split(mark*2, 1)
		if(temp == [""]):
			return (text, len(text))
		skip = len(temp[0]) + 3
		body = "<{1}>{0}</{1}>".format(self.process(text[2:skip-1]), tag)
		return (body,skip)
	
	'''
	Handles the heading tag for text
	'''
	def handleHeading(self, line):
		levels = 0
		end = 0
		for i, c in enumerate(line):
			if(c in "=" and end == 0):
				levels += 1
			elif(c not in "="):
				end = i
			else:
				break
		esc_string = escape(line[levels:end+1])
		return "<h{0} id='toc_{2}'>{1}</h{0}>\n".format(str(levels), esc_string, esc_string.replace(" ", "_"))
	
	'''
	Parses links into html hyperlinks
	'''
	def handleLink(self, line):
		line
		text = line[2:].split("]]",1)[0].split("|",1)
		skip = len("|".join(text))+4
		if(skip==0):
			return ("",0)
		output = "<a href='{0}'{1}>{2}</a>"
		name = text[0]
		link = ""
		linkClass = ""
		if(self.link_path_func != None):
			link = self.link_path_func(text[0]) + link
		if(len(text)==2):
			if(text[1] != ""):
				name = self.process(text[1])
		if(not ("://" in link or "www." in link)):
			if(self.link_class_func != None):
				LC = self.link_class_func(link)
				if(LC != None):
					linkClass = " class='{0}'".format(LC)
			link = self.link_path + link.replace(" ","_")
		elif(self.out_link_mark != ""):
			name += self.out_link_mark
		return (output.format(link,linkClass,name), skip-1)
	
	'''
	Inserts an image onto the html page
	'''
	def handleImage(self, line):
		doLink = False
		text = line[2:].split("}}",1)[0].split("|",1)
		if(text[0][0] == "{"):
			return self.handlePreformat(line)
		skip = len("|".join(text))+4
		if(skip > 0):
			output = "<img src='{0}' alt='{1}'{2}>"
			image = self.image_path + text[0]
			altText = text[0]
			opts = ""
			if(len(text) > 1):
				for i, opt in enumerate(text[1].split(";")):
					if(i==0 and opt != ""):
						altText = opt
					if(opt == "link"):
						doLink = True
					temp = opt.split("=")
					if(len(temp)!=2): continue
					temp[0] = temp[0].lower()
					if(temp[0] in "h"):
						opts += " height='{0}'".format(temp[1])
					elif(temp[0] in "w"):
						opts += " width='{0}'".format(temp[1])
					elif(temp[0] in "c"):
						opts += " class='{0}'".format(temp[1])
			output = output.format(image, altText, opts)
			if(doLink):
				output = "<a href='{0}'>{1}</a>".format(image, output)
			return (output,skip-1)
		return ("",0)
	
	'''
	Handles paragraph formatting marks
	'''
	def handleParagraph(self, line):
		offset = 2
		res = rematch(regex_indent, line)
		indent = 0
		mark = ""
		if(res != None):
			indent = len(res.group())
			offset = indent + 1
			mark = line[indent]
		else:
			mark = line[1]
		if(mark in "<>_="):
			ret = "<p style='text-align:{0}'>{1}</p>\n".format({
					"<": "left",
					">": "right",
					"_": "center",
					"=": "justify"
				}[mark],
				self.process(line[offset:])
			)
		else:
			ret = "<p>{0}</p>\n".format(self.process(line[indent:]))
		if(indent > 0):
			return "<div style='margin-left:{0}px;'>\n{1}</div>".format(indent*20, ret)
		else:
			return ret
	
	'''
	Handler function for definition lists
	'''
	def handleDefinitionLists(self, text):
		output = ["<dl>"]
		lines = text.split("\n")
		while(len(lines) > 0):
			output += ["<dt>" + self.process(lines[0][1:]) + "</dt>"]
			output += ["<dd>" + self.process(lines[1][1:]) + "</dd>"]
			del lines[:2]
		output += ["</dl>"]
		return "\n".join(output)
			
	'''
	Handler function for bullet, numbered, lettered, and roman numeral lists
	'''	
	def handleLists(self, text):
		lines = []
		for line in text.split("\n"):
			if(rematch(regex_list, line) == None):
				break
			else:
				lines += [line]
		return "".join(self.handleListsSub(lines))
	
	def handleListsSub(self, lines):
		mark = lines[0][0]
		level = self.listMarkCount(lines[0])
		num = 0
		
		startTags = {"*":"<ul>","#":"<ol>","@":"<ol type='A'>", "!":"<ol type='I'>"}
		endTags = {"*":"</ul>","#":"</ol>","@":"</ol>", "!":"</ol>"}
		
		yield startTags[mark]
		opened = [endTags[mark]]
		
		listMarkCount = self.listMarkCount
		process = self.process
		
		for i in range(0, len(lines)):
			line = lines[i]
			level = listMarkCount(lines[i])
			mark = line[0]
			yield "<li>" + process(line[level+1:])
			
			if(i+1 < len(lines)):
				nlevel = listMarkCount(lines[i+1])
				nmark = lines[i+1][0]
				if(nlevel != level):
					if(nlevel > level):
						yield "\n" + (startTags[nmark] * (nlevel - level))
						opened = ([endTags[nmark]] * (nlevel - level)) + opened
					elif(nlevel < level):
						yield "</li>\n"
						for x in range(0,level - nlevel):
							yield "\n" + opened[0]
							del opened[0]
						if(nmark != mark):
							if(opened[0] != endTags[nmark]):
								yield opened[0] + "\n", startTags[0]
								opened[0] = endTags[nmark]
				elif(nmark != mark):
					yield "</li>\n" + startTags[nmark]
					opened[0] = [endTags[nmark]]
				else:
					yield "</li>"
			else:
				yield "</li>" + "".join(opened) + "\n"
			
			#output += o
			num += 1
		#return ("".join(output), num, len("\n".join(lines)))
			
	
	def listMarkCount(self, line):
		res = rematch(regex_list2,line)
		if(res == None):
			return 0
		return len(res.groups()[0])
	
	'''
	Handles preformat blocks, where text is not formatted and formatting marks are kept verbatim
	'''
	def handlePreformat(self, text):
		end = text.find("}}}")
		if(end != -1):
			return ("<code>{0}</code>".format(escape(text[3:end]),True), end+2)
		return ("",0)
	
	'''
	Handles the rendering of HTML tables
	'''
	def handleTables(self, text):
		lines=[]
		for line in text.split("\n"):
			if(line == "" or line[0] not in "|"):
				break
			lines+=[line]
		skip = len("\n".join(lines))
		if(skip > 0):
			output=["<table>"]
			for line in lines:
				if(line[-1] in "|"):
					line = line[1:-1]
				else:
					line = line[1:]
				
				'''
				bracks=0
				cells=[]
				start=-1
				length = len(line)-1
				for i, c in enumerate(line):
					if(start==-1):
						start=i
					if(i>0):
						prev = line[i-1]
						if(c == prev):
							if(c in "{[<"):
								bracks+=1
							elif(c in "}]>"):
								if(bracks > 0):
									bracks-=1
						if(c in "|" and bracks == 0):
							cells += [line[start:i]]
							start=-1
					if(i == length):
						cells += [line[start:]]
				'''
				
				cells = re.split("\|(?!(?:(?!\[\[).)*\]\])(?!(?:(?!\{\{).)*\}\})(?!(?:(?!\<\<).)*\>\>)", line, flags=re.VERBOSE)
				
				output+=["  <tr>"]
				for cell in cells:
					if(cell!=""):
						output+=self.handleTableCell(cell)
				output+=["  </tr>"]
			output+=["</table>"]
			return "\n".join(output)
		return ""
	'''
	Handles an individual table cell
	'''
	def handleTableCell(self, cell):
		output = "    <{0}{1}>{2}</{0}>"
		colspan = ""
		tag = "td"
		if(cell[0] == "="):
			tag = "th"
			cell = cell[1:]
		span = 0
		for c in cell:
			if(c != "+"):
				break
			span += 1
		if(span > 0):
			cell = cell[span:]
			colspan = " colspan='{0}'".format(span+1)
		return [output.format(tag, colspan, self.process(cell))]
	
	'''
	Handler function for macros
	'''
	def handleMacro(self, text):
		level = 0
		macro = []
		iNum=0
		iNum2=-1
		for i,c in enumerate(text):
			if(i==0): continue
			if(c=="<"==text[i-1]):
				level += 1
			if(c==">"==text[i-1]):
				level -= 1
			if(level == 0):
				iNum=i
				macro = text[2:i-1].split(" ",1)
				break
		
		if(iNum > 0):
			body=""
			macroError = "<em><b>MACRO ERROR: {0} </b></em> "# + escape("<")
			length = len(text[:iNum])
			try: func = self.non_bodied_macros[macro[0]]
			except: func = None
			
			if(func == None):
				try: func = self.bodied_macros[macro[0]]
				except: return (macroError.format("could not find " + macro[0]), length)
				iNum2 = self.findMacroEnd(macro[0], text)
				if(iNum2 == -1):
					return (macroError.format("Bodied macros must have closing tags!"), length)
				body = text[iNum+1:iNum2]
				length = iNum2 + len("<</{0}>>".format(macro[0]))
			if(self.noMacros):
				return (text[:length+1], length)
			pos, kw = [], {}
			if(len(macro) > 1):
				params = shlex.split(macro[1])
				temp = inspect.getargspec(func)
				try:
					positionals = len(temp[0]) - len(temp[-1]) - 1
				except:
					positionals = 0
				for param in params:
					if(positionals > 0):
						if("=" in param): pos += [param.split("=",1)[-1]]
						else: pos += [param]
						positionals -= 1
					else:
						if("=" in param):
							arg = param.split("=")
							kw[arg[0]] = arg[1]
						elif(len(kw)==0):
							pos += [param]
						else:
							return (macroError.format("bad macro argument for {0}: {1}".format(macro, escape(param, True))), length)
			mco = MacroObject(body=body, renderer=self.render)
			ret = func(mco, *pos, **kw)
			if(ret == ""):
				ret = 0
			return (ret, length)
		return ("",0)
	
	'''
	Used to find the closing marks of a macro
	'''
	def findMacroEnd(self, macro, text):
		length = len(macro)
		skip = True
		counter=1
		for i, c in enumerate(text):
			if(c == ">" == text[i-1]):
				if(skip == True):
					skip = False
					continue
				if(text[i-length-1:i-1] == macro):
					if(text[i-length-3:i-length-1] == "<<"):
						counter += 1
					elif(text[i-length-4:i-length-1] == "<</"):
						counter -= 1
					if(counter == 0):
						return i-length-4
		return -1

	'''
	Built-in macro for inserting the current time and date
	'''
	def macro_datetime(self,macro,timeString="%Y-%m-%d %H:%M:%S"):
		return datetime.datetime.now().strftime(timeString)

	'''
	Built-in macro for inserting an html block such as div or span to the page
	'''
	def macro_block(self,macro,blockType="div",cssclass=None,cssid=None,style=None):
		body = self.render(macro.body)
		out = ["<{0}".format(blockType)]
		if(cssid!=None):
			out += [" id='{0}'".format(cssid)]
		if(cssclass!=None):
			out += [" class='{0}'".format(cssclass)]
		if(style!=None):
			out += [" style='{0}'".format(style)]
		out += [">{0}</{1}>".format(body,blockType)]
		return "".join(out)


pageTemp = '''
<!DOCTYPE html>
<html lang='en'>
	<head>
		<title>DragonCreole Test</title>
		<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
		<link rel="stylesheet" type="text/css" href=/media/theme.css>
	</head>
	<body>
		{0}
	</body>
</html>
'''

#Testing code, requires that Flask be installed.
if __name__ == "__main__":
	from flask import Flask
	app = Flask(__name__, static_folder="media")
	
	parser = DragonCreole(
		image_path="media/",
		link_class_func=None,
	)
	
	@app.route("/")
	@app.route("/index")
	def page():
		with open("test.txt", "r") as f:
			return pageTemp.format(parser.render(f.read()))
	
	app.run(debug=True, port=5000)
	#app.run(debug=True, port=5000, host="0.0.0.0")
