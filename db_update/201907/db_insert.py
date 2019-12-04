import pandas as pd
import os
import numpy as np
import sqlite3

conn = sqlite3.connect("food.db")
cur = conn.cursor()

# 숫자와 카테고리 이름 매칭에 따른 리스트 생성
categorys = ["", "seasoned_foods", "noodles", "egg_included_processed_products", "edible_oil_and_fat", "rice_cake", "tofu_or_jellied_foods", "meat", "special_purpose_food", "fish_meat_processed_products", "confectionery_frozen_dessert", "instant_food", "beverages"]

for category in categorys:
	try:
		# 규칙에 맞춰 정리한 food_list 엑셀을 읽어서 값들을 입력한다.
		# 2018년과 비교해 전부 신규 카테고리이기 때문에 id 신경쓰지 않고 그냥 입력
		excel_data = pd.read_excel("201907_food_list_v2.xlsx", sheet_name=category)
		excel_data2 = excel_data.where((pd.notnull(excel_data)), None)

		for index, row in excel_data2.iterrows():
			try:
			    cur.execute("INSERT INTO list (category, id, name) VALUES (?, ?, ?)", [category, int(row['id']), row['name']] )
			    conn.commit()

			    cur.execute("INSERT INTO information (category, id, amount, calorie, carbohydrate, fat, protein, natrium, portion) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", [category, int(row['id']), row['amount'], row['calorie'], row['carbohydrate'], row['fat'], row['protein'], row['natrium'], row['portion']] )
			    conn.commit()

			except Exception as e:
				print(category, index, row, e)

	except Exception as e:
		print(category, e)

# ir 데이터 입력 시작 
files = os.listdir("ir_data")

for file in files:		
	try:
		excel_data = pd.read_excel("ir_data/" + file)

		pid = file.split(".")[0]
		s = pid.split("-")
		cid = int(s[1])
		category = categorys[int(s[0])]

		cnt = 0
		mean = np.zeros(256)

		for col in excel_data:
			# 경북대에서 보내준 엑셀 파일들의 양식이 일치하지 않기 때문에 예외처리가 필요함
			if col == "Unnamed: 0":
				continue
			cnt+=1
			for idx, row in enumerate(excel_data[col]):
				mean[idx] += row
		mean /= cnt		

		# ir_data 테이블 값은 사용하지 않고 5개의 평균을 사용하는 ir_data_mean만 사용함
		for idx, v in enumerate(mean.tolist()):
			cur.execute("INSERT INTO ir_data_mean (category, id, range, data) VALUES (?, ?, ?, ?)", [category, cid, idx, v])
			conn.commit()

	except Exception as e:
		print(e)

