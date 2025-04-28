from statistics import median
import time
from pprint import pprint
from progressbar import ProgressBar
import random
import numpy as np
import pandas as pd
from collections import Counter


atribute_and_order = {
	"name": 0,
	"niche-url-name": 1,
	"religious-affiliation": 2,
	"city": 3,
	"state": 4,
	"niche-grade": 5,
	"sat-consideration": 6,
	"gpa-consideration": 7,
	"first-descriptive-student-word": 8,
	"second-descriptive-student-word": 9,
	"third-descriptive-student-word": 10,
	"first-descriptive-college-word": 11,
	"second-descriptive-college-word": 12,
	"third-descriptive-college-word": 13,
	"academics-grade": 14,
	"value-grade": 15,
	"campus-grade": 16,
	"party-scene-grade": 17,
	"location-grade": 18,
	"campus-food-grade": 19,
	"safety-grade": 20,
	"professors-grade": 21,
	"dorms-grade": 22,
	"student-life-grade": 23,
	"price": 24,
	"num-of-students": 25,
	"num-of-comp-sci-students": 26,
	"city-size?": 27,
	"comp-sci-rank": 28,
	"num-of-reviews": 29,
	"athletic-division": 30,
	"acceptance-rate": 31,
	"sat-min": 32,
	"sat-max": 33,
	"application-fee": 34,
	"%-receiving-aid": 35,
	"avg-aid": 36,
	"student-faculty-ratio": 37,
	"num-of-descriptive-student-word-responses": 38,
	"%-point-differential-for-first-and-second-student-words": 39,
	"num-of-descriptive-college-word-responses": 40,
	"%-point-differential-for-first-and-second-college-words": 41,
	"%-live-on-campus": 42,
	"graduation-rate": 43,
	"2-yr-employment": 44,
	"median-earnings-6-yrs-after": 45,
	"%-confident-they-can-find-a-job": 46,
	"num-of-responses-to-confidence-finding-job": 47,
	"%-of-1-star-reviews": 48,
	"%-of-2-star-reviews": 49,
	"%-of-3-star-reviews": 50,
	"%-of-4-star-reviews": 51,
	"%-of-5-star-reviews": 52,
	"star-rating": 53,
	"4-yr": 54,
	"early-decision": 55,
	"sat-in-range": 56,
	"sat-at-least": 57,
	"comp-sci-in-top-5": 58,
	"diversity-grade": 59,
	"athletics-grade": 60,
	"majors-link": 61,
	"description": 62,
	"short-name": 63,
	"all-women": 64,
	"accepts-common-app": 65,
	"is-online": 66,
	"min-major-num": 67
}


def read_data():
	df = pd.DataFrame(columns=atribute_and_order.keys())
	with open("formatted_data.txt") as f:
		raw_data = f.readlines()
	for i in range(len(raw_data)):
		raw_data[i] = raw_data[i].split("<split>")
	z=0
	for i in raw_data:
		if len(i)<68:
			z+=1
	for i in raw_data:
		df.loc[len(df.index)] = ({
			"name": i[0],
			"niche-url-name": i[1],
			"religious-affiliation": i[2],
			"city": i[3],
			"state": i[4],
			"niche-grade": i[5],
			"sat-consideration": i[6],
			"gpa-consideration": i[7],
			"first-descriptive-student-word": i[8],
			"second-descriptive-student-word": i[9],
			"third-descriptive-student-word": i[10],
			"first-descriptive-college-word": i[11],
			"second-descriptive-college-word": i[12],
			"third-descriptive-college-word": i[13],
			"academics-grade": i[14],
			"value-grade": i[15],
			"campus-grade": i[16],
			"party-scene-grade": i[17],
			"location-grade": i[18],
			"campus-food-grade": i[19],
			"safety-grade": i[20],
			"professors-grade": i[21],
			"dorms-grade": i[22],
			"student-life-grade": i[23],
			"price": int(i[24]),
			"num-of-students":int(i[25]),
			"num-of-comp-sci-students":int(i[26]),
			"city-size?":int(i[27]),
			"comp-sci-rank":int(i[28]),
			"num-of-reviews":int(i[29]),
			"athletic-division": i[30],
			"acceptance-rate":int(i[31]),
			"sat-min":int(i[32]),
			"sat-max":int(i[33]),
			"application-fee":int(i[34]),
			"%-receiving-aid":int(i[35]),
			"avg-aid":int(i[36]),
			"student-faculty-ratio": i[37],
			"num-of-descriptive-student-word-responses": i[38],
			"%-point-differential-for-first-and-second-student-words": i[39],
			"num-of-descriptive-college-word-responses": i[40],
			"%-point-differential-for-first-and-second-college-words": i[41],
			"%-live-on-campus":int(i[42]),
			"graduation-rate":int(i[43]),
			"2-yr-employment":int(i[44]),
			"median-earnings-6-yrs-after":int(i[45]),
			"%-confident-they-can-find-a-job":int(i[46]),
			"num-of-responses-to-confidence-finding-job":int(i[47]),
			"%-of-1-star-reviews":float(i[48]),
			"%-of-2-star-reviews": float(i[49]),
			"%-of-3-star-reviews": float(i[50]),
			"%-of-4-star-reviews": float(i[51]),
			"%-of-5-star-reviews": float(i[52]),
			"star-rating": float(i[53]),
			"4-yr": i[54] == "True",
			"early-decision": i[55] == "True",
			"sat-in-range": i[56] == "True",
			"sat-at-least": i[57] == "True",
			"comp-sci-in-top-5": i[58] == "True",
			"diversity-grade": i[59],
			"athletics-grade": i[60],
			"majors-link": i[61],
			"description": i[62],
			"short-name": i[63],
			"all-women": i[64] == "True",
			"accepts-common-app": i[65] == "True",
			"is-online":i[66][:-1] == "True",
			"min-major-num": int(i[67])
		})
	return df


df = read_data()


df = df[df["religious-affiliation"]=="s"]
# df = df[df["state"] != "NY"]
df = df[df["comp-sci-rank"] <= 100]
# df = df[df["price"]<=30000]
# df = df[df["is-online"] == False]
df = df[df["all-women"] == False]
# df = df[df["4-yr"] == True]
# df = df[df["%-receiving-aid"] >= 50]
df = df[df["num-of-students"] >= 7000]
# df = df[df["city"] == "Philadelphia"]
df = df[df["sat-at-least"]]
pprint(df[["short-name", "comp-sci-rank", "num-of-students","price","niche-grade","sat-min"]])
print(len(df))
# cities = df["city"]
# pprint(Counter(cities).most_common(20))
 