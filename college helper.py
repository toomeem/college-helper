'''
59 columns
add "majors/" to URL to get to majors page
data file format:
	attributes seperated by comma and ending in ;\n
	spaces relaced with dashes
'''

import time
from pprint import pprint
import requests
from bs4 import BeautifulSoup
from progressbar import ProgressBar
import random
import re

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
  		"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
  		"Mozilla/5.0 (Macintosh; Intel Mac OS X 12.4; rv:102.0) Gecko/20100101 Firefox/102.0",
  		"Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko",
  		"Mozilla/5.0 (X11; CrOS x86_64 14816.99.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36",
  		"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 Edg/103.0.1264.49"]
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
	"SAT-in-range": 56,
	"SAT-at-least": 57,
	"comp-sci-in-top-5": 58,
	"diversity-grade": 59,
	"athletics-grade": 60,
	"majors-link": 61
}


def is_status_fatal(status, url):
	if status == 404:
		print("404 page does not exist")
		print(f"url: {url}")
		return False
	elif status == 403:
		print("403 FORBIDDEN")
		return True
	elif status == 429:
		print("429 too many requests")
		return False
	elif status >= 400:
		print(f"{status} error")
		return True
	elif status == 200:
		return False
	else:
		print(status)
		return False


def get_soup(url):
	header = {'User-Agent': random.choice(user_agents)}
	r = requests.get(url, headers=header)
	status = r.status_code
	if is_status_fatal(status, url):
		return False, status
	return BeautifulSoup(r.text, 'html.parser'), status


def is_num(num):
	try:
		float(num)
		return True
	except ValueError:
		return False


def remove_nums(s):
	s = [i for i in s]
	new_str = ""
	for i in s:
		if not is_num(i):
			new_str += i

	return new_str


# print("Would you like to get the college links? (y/n)")
get_links = False  # input() == "y"
# print("Would you like to get the college data? (y/n)")
get_data = False  # input() == "y"


# URL collection
links = []

if get_links:
	rate_wait = 10
	status = 200
	for num in range(1, 21):
		if rate_wait > 20:
			print("too many rate limits")
			print("rate wait:", rate_wait)
			break
		url = "https://www.niche.com/colleges/search/best-colleges-for-computer-science/?type=private&type=public"
		if num != 1:
			url += f"&page={num}"
		time.sleep(rate_wait+random.random()-0.5)
		ranking_soup, status = get_soup(url)
		if not ranking_soup:
			break
		elif status == 429:
			rate_wait *= 2
			print(f"Waiting {rate_wait} seconds between requests")
		elif status == 404:
			continue
		link = ranking_soup.find_all(
			"a", "MuiTypography-root MuiTypography-inherit MuiLink-root MuiLink-underlineNone search-result__link css-1dbsl7y")
		for i in link:
			links.append(i.get("href"))
		print(num)

	print(f"{len(links)} links found")
	with open("college_links.txt", "w") as f:
		for i in links:
			f.write(i+"\n")


# data scraping
with open("college_links.txt", "r") as f:
	links = f.readlines()
soups_list = []
if get_data:
	rate_wait = 10
	status = 200
	num = 1
	for link in links:
		link = link[:-1]
		if rate_wait > 20:
			print("too many rate limits")
			print("rate wait:", rate_wait)
			break
		time.sleep(rate_wait+random.random()-0.5)
		soup, status = get_soup(link)
		if not soup:
			break
		elif status == 429:
			rate_wait *= 2
			print(f"Waiting {rate_wait} seconds between requests")
			continue
		elif status == 404:
			continue
		else:
			print(status)
		soups_list.append(str(soup))
		with open("soup.txt", "wb") as f:
			f.write(str(soup).encode())
		num += 1
		if num == 2:
			break
soups_list = str(soups_list)
with open("college_soups.txt", "wb") as f:
	f.write(soups_list.encode())
with open("college_soups.txt", "rb") as f:
	soups = f.read().decode()

with open("soup.txt", "rb") as f:
	soup = BeautifulSoup(f.read().decode(), 'html.parser')
name = soup.find("h1", "postcard__title").text
niche_url_name = str(re.search('rl":".+","isClai', str(soup)
                               ).group().split('","isClai')[0])[5:]
religious_afilliation = "c" if str(
	soup).lower().count("christian") > 2 else "s"
if "jewish" in str(soup):
	religious_afilliation = "j"
city, state = soup.find_all(
	"li", "postcard__attr postcard-fact")[1].text.split(", ")
niche_grade = str(soup.find("div", "overall-grade__niche-grade").text[-2:])
sat_consideration = soup.find_all("div", "scalar--three")[3].text[7:]
gpa_consideration = soup.find_all("div", "scalar--three")[4].text[15:]
student_words = soup.find_all(
	"div", "poll__table__result__label")[:3]
first_descriptive_student_word = student_words[0].text
second_descriptive_student_word = student_words[1].text
third_descriptive_student_word = student_words[2].text
del student_words
college_words = soup.find(
	"div", "poll__table--bar_chart--bar_chart_color").text.split("Report")[1].split("%")[:3]
first_descriptive_college_word = remove_nums(college_words[0])
second_descriptive_college_word = remove_nums(college_words[1])
third_descriptive_college_word = remove_nums(college_words[2])
del college_words
grades = soup.find_all("li", "ordered__list__bucket__item")
academics_grade = grades[0].text.replace(
	"Academicsgrade\xa0", "").replace(" minus", "-")
value_grade = grades[1].text.replace(
	"Valuegrade\xa0", "").replace(" minus", "-")
diversity_grade = grades[2].text.replace(
	"Diversitygrade\xa0", "").replace(" minus", "-")
campus_grade = grades[3].text.replace(
	"Campusgrade\xa0", "").replace(" minus", "-")
athletics_grade = grades[4].text.replace(
	"Athleticsgrade\xa0", "").replace(" minus", "-")
party_scene_grade = grades[5].text.replace(
	"Party Scenegrade\xa0", "").replace(" minus", "-")
professors_grade = grades[6].text.replace(
	"Professorsgrade\xa0", "").replace(" minus", "-")
location_grade = grades[7].text.replace(
	"Locationgrade\xa0", "").replace(" minus", "-")
dorms_grade = grades[8].text.replace(
	"Dormsgrade\xa0", "").replace(" minus", "-")
campus_food_grade = grades[9].text.replace(
	"Campus Foodgrade\xa0", "").replace(" minus", "-")
student_life_grade = grades[10].text.replace(
	"Student Lifegrade\xa0", "").replace(" minus", "-")
safety_grade = grades[11].text.replace(
	"Safetygrade\xa0", "").replace(" minus","-")
del grades
price = soup.find_all("section", "block--two-two")
for i in price:
	if "Net Price" in i.text:
		price = i
		break
price = price.contents[1].contents[0].contents[0].contents[0].contents[1]
price = int(price.contents[0].string[1:].replace(",", ""))
student_num = soup.find_all("section", "block--two")
for i in student_num:
	if "Full-Time Enrollment" in i.text:
		student_num = i
		break
student_num = student_num.contents[1].contents[0].contents[0].contents[0].contents[1]
student_num = int(student_num.contents[0].string.replace(",", ""))
comp_sci_student_num = None
city_size = None
comp_sci_rank = None
num_of_reviews = int(soup.find("span", "review__stars__number__reviews").text.replace(" reviews", "").replace(",", ""))
athletic_division = soup.find_all("div", "profile__bucket--2")
for i in athletic_division:
	if "Athletic Division" in i.text:
		athletic_division = i
		break
athletic_division = athletic_division.contents[0].contents[1].contents[1].string
acceptance_rate = soup.find_all("div", "scalar")
for i in acceptance_rate:
	if "Acceptance Rate" in i.text:
		acceptance_rate = i
		break
acceptance_rate = int(acceptance_rate.contents[1].string[:-1])
sat_range = soup.find_all("div", "scalar--three")
for i in sat_range:
	if "SAT Range" in i.text:
		sat_range = i
		break
sat_range = sat_range.contents[1].text.split("-")
sat_min = int(sat_range[0])
sat_max = int(sat_range[1])
application_fee = soup.find_all("div", "scalar--three")
for i in application_fee:
	if "Application Fee" in i.text:
		application_fee = i
		break
application_fee = int(application_fee.contents[1].text[1:])
percent_receiving_aid = soup.find_all("div", "scalar--three")
for i in percent_receiving_aid:
	if "Students Receiving Financial Aid" in i.text:
		percent_receiving_aid = i
		break
percent_receiving_aid = int(percent_receiving_aid.contents[1].text[:-1])
avg_aid = soup.find_all("div", "scalar--three")
for i in avg_aid:
	if "Average Total Aid Awarded" in i.text:
		avg_aid = i
		break
avg_aid = int(avg_aid.contents[1].contents[0].text[1:].replace(",", ""))


# print("DONE")
