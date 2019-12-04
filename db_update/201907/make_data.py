import os
import shutil
from PIL import Image

# 숫자와 카테고리 이름 매칭에 따른 리스트 생성
categorys = ["", "seasoned_foods", "noodles", "egg_included_processed_products", "edible_oil_and_fat", "rice_cake", "tofu_or_jellied_foods", "meat", "special_purpose_food", "fish_meat_processed_products", "confectionery_frozen_dessert", "instant_food", "beverages"]
folders = ["exterior", "interior"]

counter = dict()

for folder in folders:
	l = [0] * (len(categorys) + 1)
	if not os.path.exists("result/" + folder):
		os.mkdir("result/" + folder)
	files = os.listdir(folder)
	for file in files:
		s = file.split("-")
		#파일명의 앞부분은 카테고리 번호를 의미함
		t = categorys[int(s[0])]
		l[int(s[0])] += 1

		if not os.path.exists("result/" + folder + "/" + t):
			os.mkdir("result/" + folder + "/" + t)

		src = folder + "/" + file
		#파일명의 뒷부분은 해당 카테고리에서의 id를 의미
		trg = "result/" + folder + "/" + t + "/" + s[1] 

		img = Image.open(src)
		size = img.size
		#width 500픽셀을 기준으로 리사이즈 한다.
		height = int(size[1] * 500/size[0])
		img.resize((500, height)).save(trg)
