import tabula
import pprint
import re
import PyPDF2
from tika import parser

def parse_pdf(file):
    raw = parser.from_file(file)
    text = str(raw['content'])
    safe_text = text.encode('utf-8', errors='ignore')
    po = re.search("BONDS/.*", text)
    date = re.search("Date:.*", text)
    title = re.search("TITLE :.*", text)
    quot = re.search("Quot. :.*", text)
    contact = re.search("Supplier's Contact.*", text)
    # print(type(safe_text))
    print(po.group())
    print(date.group().split(": ")[1])
    print(title.group().split(":")[1])
    print(quot.group().split(":")[1])
    print(contact.group())
    return 'Hello'

def extract_information(file):
	df = tabula.read_pdf(file, output_format="json", pages="all", lattice=True,)
	# in order to print first 5 lines of Table
	# print(df)
	sl = []
	item_name = []
	item_details = []
	quantity = []
	amount = []
	unit_price = []
	for k in range(0,len(df)):
		for i in range(1,len(df[k]['data'])):
			for j in range(len(df[k]['data'][i])):
				if j == 0:
					continue
				elif j == 1:
					if len(df[k]['data'][i][j]['text']) > 0:
						item_name.append(df[k]['data'][i][j]['text'])
						# pprint.pprint(df[k]['data'][i][j]['text'])
					else:
						continue
				elif j == 2:
					if len(df[k]['data'][i][j]['text']) > 0:
						item_details.append(df[k]['data'][i][j]['text'])
					else:
						continue
				elif j == 3:
					if len(df[k]['data'][i][j]['text']) > 0:
						quantity.append(df[k]['data'][i][j]['text'])
					else:
						continue
				elif j == 4:
					if len(df[k]['data'][i][j]['text']) > 0:
						unit_price.append(df[k]['data'][i][j]['text'])
					else:
						continue
				else:
					if len(df[k]['data'][i][j]['text']) > 0:
						amount.append(df[k]['data'][i][j]['text'])
					else:
						continue
	pprint.pprint(item_name)
	pprint.pprint(item_details)
	pprint.pprint(quantity)
	pprint.pprint(unit_price)
	pprint.pprint(amount)
if __name__ == '__main__':
    path = 'C:/Users/X-WAY/Downloads/23.pdf'
    extract_information(path)
    # print(parse_pdf(path))