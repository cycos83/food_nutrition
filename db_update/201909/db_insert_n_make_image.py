import pandas as pd
import os
import numpy as np
import sqlite3
from PIL import Image

conn = sqlite3.connect("food.db")
cur = conn.cursor()

# 숫자와 카테고리 이름 매칭에 따른 리스트 생성
categorys = ["", "seasoned_foods", "noodles", "egg_included_processed_products", "edible_oil_and_fat", "rice_cake", "tofu_or_jellied_foods", "meat", "special_purpose_food", "fish_meat_processed_products", "confectionery_frozen_dessert", "instant_food", "beverages"]

for category in categorys:
	try:
		# 규칙에 맞춰 정리한 food_list 엑셀을 읽어서 값들을 입력한다.
		# 10 빙과류를 제외하곤 엑셀에 ID를 맞춰서 입력해두었음(pid 참고)
		# 10 빙과류만 ID 추출후 23을 더해준다( 24부터 시작 )
		excel_data = pd.read_excel("201909_food_list_v2.xlsx", sheet_name=category)
		excel_data2 = excel_data.where((pd.notnull(excel_data)), None)

		sid = 0
		if category == "confectionery_frozen_dessert":
			sid = 23

		for index, row in excel_data2.iterrows():
			pid = row['pid'].strip()
			cid = int(pid.split("-")[1]) + sid			

			# 기본정보 입력
			try:				
			    cur.execute("INSERT INTO list (category, id, name) VALUES (?, ?, ?)", [category, cid, row['name']] )
			    conn.commit()

			    cur.execute("INSERT INTO information (category, id, amount, calorie, carbohydrate, fat, protein, natrium, portion) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", [category, cid, row['amount'], row['calorie'], row['carbohydrate'], row['fat'], row['protein'], row['natrium'], row['portion']] )
			    conn.commit()

			except Exception as e:
				print(category, index, row, e)

			# ir_data 입력
			# ir데이터 체크, 9번 항목은 9.xlsx에 몰려있음			
			ir_data = None
			if pid.split("-")[0] == "9":
				try:
					ir_data = pd.read_excel("ir_data/9.xlsx", sheet_name=pid)
				except Exception as e:
					print(pid, "no ir data")
			else:
				if not os.path.exists("ir_data/" + pid + ".xlsx"):
					print(pid, "no ir data")
				else:
					ir_data = pd.read_excel("ir_data/" + pid + ".xlsx")

			if not ir_data is None:				
				# data check에서 ir 데이터가 5*256개 있는지 다 체크함
				mean = np.zeros(256)
				for col in ir_data:
					for idx in range(256):
						mean[idx] += ir_data.iloc[idx][col]
				mean /= 5
				try:
					# ir_data 테이블 값은 사용하지 않고 5개의 평균을 사용하는 ir_data_mean만 사용함
					for idx, v in enumerate(mean.tolist()):
						cur.execute("INSERT INTO ir_data_mean (category, id, range, data) VALUES (?, ?, ?, ?)", [category, cid, idx, v])
						conn.commit()
				except Exception as e:
					print("ir INSERT ERROR:", pid)

			# 내부 외부 이미지 리사이즈 
			folders = ["exterior", "interior"]
			if not os.path.exists("result"):
				os.mkdir("result")			
			for folder in folders:
				if not os.path.exists("result/" + folder):
					os.mkdir("result/" + folder)
				if not os.path.exists("result/" + folder + "/" + category):
					os.mkdir("result/" + folder + "/" + category)

				src = folder + "/" + pid + ".jpg"
				tar = "result/" + folder + "/" + category + "/" + str(cid) + ".jpg"

				if not os.path.exists(src):
					continue

				img = Image.open(src)
				size = img.size
				#width 500픽셀을 기준으로 리사이즈 한다.
				height = int(size[1] * 500/size[0])
				img.resize((500, height)).save(tar)
				
	except Exception as e:
		print(category, e)