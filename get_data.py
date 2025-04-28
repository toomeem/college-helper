import time
from pprint import pprint
import requests
from bs4 import BeautifulSoup
from progressbar import ProgressBar
import random

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
  		"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
  		"Mozilla/5.0 (Macintosh; Intel Mac OS X 12.4; rv:102.0) Gecko/20100101 Firefox/102.0",
  		"Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko",
  		"Mozilla/5.0 (X11; CrOS x86_64 14816.99.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36",
  		"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 Edg/103.0.1264.49"]


def is_status_fatal(status):
	if status == 404:
		print("404 page does not exist")
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
	if is_status_fatal(status):
		print(url)
		return False, status
	return r.text.encode("ASCII", "ignore").decode("ASCII"), status


def remove_nums(s):
	s = [i for i in s if not i.isnumeric()]
	return "".join(s)


def to_int(x):
	x = [i for i in str(x) if i.isnumeric()]
	return int("".join(x))


def contents(tag, nums):
	for i in nums:
		tag = tag.contents[i]
	return tag


print("Would you like to get the college links? (y/n)")
get_links = input() == "y"
print("Would you like to get the college pages? (y/n)")
get_data = input() == "y"
start = 0
if get_data:
	print("What page would you like to start on?")
	start = int(input())
print("Would you like to prepare the data? (y/n)")
format_data = input() == "y"
print("\n")

# URL collection
if get_links:
	pbar = ProgressBar(21).start()
	links = []
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
		pbar.update(num)
	pbar.finish()
	print(f"{len(links)} links found")
	with open("college_links.txt", "w") as f:
		for i in links:
			f.write(i+"\n")

# data scraping
if get_data:
	pbar = ProgressBar(len(link)+1).start()
	rate_wait = 15
	status = 200
	if start == 0:
		with open("college_soups.txt", "w") as f:
			pass
	with open("college_links.txt", "r") as f:
		links = f.readlines()
	for i in range(start, len(links)):
		link = links[i][:-1]
		time.sleep(rate_wait+random.random()-0.5)
		soup, status = get_soup(link)
		if not soup or status == 429:
			print(f"page num: {i}")
			break
		elif status == 404:
			continue
		else:
			pbar.update(i)
			# print(i, link[31:-1])
			soup = str(soup)
			with open("college_soups.txt", "a") as f:
				f.write(str(soup).replace("\n", "")+"\n")
	pbar.finish()

# data parsing and organizing
if format_data:
	with open("college_links.txt", "r") as f:
		links = f.readlines()
	pbar = ProgressBar(len(links)+1).start()
	with open("college_soups.txt", "r") as f:
		soups = f.readlines()
	with open("formatted_data.txt", "w") as f:
		pass
	for i in range(len(soups)):
		soup = BeautifulSoup(soups[i], "html.parser")
		link = links[i][:-1]
		name = contents(
			soup.find("div", "postcard__content postcard__content--primary"), [0]).text
		niche_url_name = links[i][31:-2]
		try:
			soup.find("a", "tooltip-trigger__claimed-check tooltip-trigger")
			is_claimed = True
		except:
			is_claimeed = False
		try:
			description = soup.find("span", "bare-value").text
		except:
			pass
		try:
			description = soup.find("p", "premium-paragraph__text").text
		except:
			description = None
		short_name = soup.find("div", "search-tags__label").text[6:-3]
		pbar.update(i)
		search_tags = soup.find("ul", "search-tags__wrap__list").text
		if search_tags.count("Catholic") != 0:
			religious_affiliation = "c"
		elif search_tags.count("Christian") != 0:
			religious_affiliation = "c"
		elif search_tags.count("Jewish") != 0:
			religious_affiliation = "j"
		else:
			religious_affiliation = "s"
		if search_tags.count("All-Women") > 0:
			all_women = True
		else:
			all_women = False
		postcard_bucket = soup.find("ul", "postcard__attrs")
		is_4_yr = contents(postcard_bucket, [0]).text == "4 Year"
		try:
			city, state = contents(postcard_bucket, [1]).text.split(", ")
			city = city.capitalize()
			is_online = False
		except:
			city, state = "Online", "na"
			is_online = True
		niche_grade = str(soup.find("div", "overall-grade__niche-grade").text.replace(" minus", "-")[-2:])
		try:
			student_words_bucket = [i for i in soup.find_all(
				"div", "poll__table--bar_chart--bar_chart_color") if "at this school?" in i.text][0]
			descriptive_student_word_responses = to_int(
				contents(student_words_bucket, [2, 0]))
			student_words_bucket = contents(student_words_bucket, [3, 0])
		except:
			pass
		try:
			first_descriptive_student_word = contents(student_words_bucket, [0, 1]).text
		except:
			first_descriptive_student_word = None
		try:
			second_descriptive_student_word = contents(
				student_words_bucket, [1, 1]).text
		except:
			second_descriptive_student_word = None
		try:
			third_descriptive_student_word = contents(student_words_bucket, [2, 1]).text
		except:
			third_descriptive_student_word = None
		try:
			diff_between_first_and_second_student_word = to_int(
				contents(student_words_bucket, [0, 2])) - to_int(contents(student_words_bucket, [1, 2]))
		except:
			diff_between_first_and_second_student_word = None
		try:
			college_words_bucket = [i for i in soup.find_all(
				"div", "poll__table--bar_chart--bar_chart_color") if "describes your school?" in i.text][0]
			descriptive_college_word_responses = to_int(
				contents(college_words_bucket, [2, 0]))
			college_words_bucket = contents(college_words_bucket, [3, 0])
		except:
			pass
		try:
			first_descriptive_college_word = contents(college_words_bucket, [0, 1]).text
		except:
			first_descriptive_college_word = None
		try:
			second_descriptive_college_word = contents(
				college_words_bucket, [1, 1]).text
		except:
			second_descriptive_college_word = None
		try:
			third_descriptive_college_word = contents(college_words_bucket, [2, 1]).text
		except:
			third_descriptive_college_word = None
		try:
			diff_between_first_and_second_college_word = to_int(
				contents(college_words_bucket, [0, 2])) - to_int(contents(college_words_bucket, [1, 2]))
		except:
			diff_between_first_and_second_college_word = -1
		grades = soup.find_all("li", "ordered__list__bucket__item")
		academics_grade = [i for i in grades if "Academics" in i.text]
		if len(academics_grade) == 0:
			academics_grade = "-"
		else:
			academics_grade = contents(academics_grade[0], [0, 1, 1]).replace(
				"unavailable", "-").replace(" minus", "-")
		value_grade = [i for i in grades if "Value" in i.text]
		if len(value_grade) == 0:
			value_grade = "-"
		else:
			value_grade = contents(value_grade[0], [0, 1, 1])
		diversity_grade = [i for i in grades if "Diversity" in i.text]
		if len(diversity_grade) == 0:
			diversity_grade = "-"
		else:
			diversity_grade = contents(diversity_grade[0], [0, 1, 1]).replace(
				"unavailable", "-").replace(" minus", "-")
		campus_grade = [i for i in grades if "Campus" in i.text]
		if len(campus_grade) == 0:
			campus_grade = "-"
		else:
			campus_grade = contents(campus_grade[0], [0, 1, 1]).replace(
				"unavailable", "-").replace(" minus", "-")
		athletics_grade = [i for i in grades if "Athletics" in i.text]
		if len(athletics_grade) == 0:
			athletics_grade = "-"
		else:
			athletics_grade = contents(athletics_grade[0], [0, 1, 1]).replace(
				"unavailable", "-").replace(" minus", "-")
		party_scene_grade = [i for i in grades if "Party Scene" in i.text]
		if len(party_scene_grade) == 0:
			party_scene_grade = "-"
		else:
			party_scene_grade = contents(party_scene_grade[0], [0, 1, 1]).replace(
				"unavailable", "-").replace(" minus", "-")
		professors_grade = [i for i in grades if "Professors" in i.text]
		if len(professors_grade) == 0:
			professors_grade = "-"
		else:
			professors_grade = contents(professors_grade[0], [0, 1, 1]).replace(
				"unavailable", "-").replace(" minus", "-")
		location_grade = [i for i in grades if "Location" in i.text]
		if len(location_grade) == 0:
			location_grade = "-"
		else:
			location_grade = contents(location_grade[0], [0, 1, 1]).replace(
				"unavailable", "-").replace(" minus", "-")
		dorms_grade = [i for i in grades if "Dorms" in i.text]
		if len(dorms_grade) == 0:
			dorms_grade = "-"
		else:
			dorms_grade = contents(dorms_grade[0], [0, 1, 1]).replace(
				"unavailable", "-").replace(" minus", "-")
		campus_food_grade = [i for i in grades if "Campus Food" in i.text]
		if len(campus_food_grade) == 0:
			campus_food_grade = "-"
		else:
			campus_food_grade = contents(campus_food_grade[0], [0, 1, 1]).replace(
				"unavailable", "-").replace(" minus", "-")
		student_life_grade = [i for i in grades if "Student Life" in i.text]
		if len(student_life_grade) == 0:
			student_life_grade = "-"
		else:
			student_life_grade = contents(student_life_grade[0], [0, 1, 1]).replace(
				"unavailable", "-").replace(" minus", "-")
		safety_grade = [i for i in grades if "Safety" in i.text]
		if len(safety_grade) == 0:
			safety_grade = "-"
		else:
			safety_grade = contents(safety_grade[0], [0, 1, 1]).replace(
				"unavailable", "-").replace(" minus", "-")
		student_num = [i for i in soup.find_all("section", "block--two") if "Full-Time Enrollment" in i.text][0]
		student_num = to_int(contents(student_num, [1, 0, 0, 0, 1, 0]).string)
		try:
			majors_bucket = [i for i in soup.find_all("div", "popular-entities") if "Popular Majors" in i.text][0]
			majors_bucket = contents(majors_bucket, [1, 0]).contents
			comp_sci_in_top = False
			for major in majors_bucket:
				if "Computer Science" in major.text:
					comp_sci_in_top = True
					comp_sci_student_num = to_int(contents(major, [0, 1]).text)
			if not comp_sci_in_top:
				comp_sci_student_num = -1
			min_major_num = to_int(contents(majors_bucket[-1], [0, 1]).text)
		except:
			comp_sci_in_top = False
			comp_sci_student_num = -1
			min_major_num = -1
		city_size = -1
		comp_sci_rank = i
		athletic_division = [i for i in soup.find_all(
			"div", "scalar--two") if "Athletic Division" in i.text][0]
		athletic_division = contents(athletic_division, [1]).string
		admissions_bucket = [i for i in soup.find_all(
			"div", "profile__buckets") if "Acceptance Rate" in i.text][0]
		try:
			acceptance_rate = to_int(
				contents(admissions_bucket, [0, 0, 0, 1]).text[:-1])
			admissions_bucket = contents(admissions_bucket, [2, 0])
			sat_range = contents(admissions_bucket, [0, 1]).text.split("-")
			sat_min = to_int(sat_range[0])
			sat_max = to_int(sat_range[1])
			application_fee = to_int(contents(admissions_bucket, [2, 1]).text)
			sat_consideration = contents(admissions_bucket, [3, 1]).text
			gpa_consideration = contents(admissions_bucket, [4, 1]).text
			has_early_decision = [i for i in soup.find_all(
				"div", "scalar--three") if "Early Decision" in i.text]
			accepts_common_app = [i for i in soup.find_all(
				"div", "scalar--three") if "Accepts Common App" in i.text]
			try:
				has_early_decision = contents(has_early_decision[0], [1]).text == "Yes"
			except:
				has_early_decision = False
			try:
				accepts_common_app = contents(accepts_common_app[0], [1]).text == "Yes"
			except:
				accepts_common_app = False
		except:
			try:
				admissions_bucket = [i for i in soup.find_all(
					"div", "profile__buckets") if "Acceptance Rate" in i.text][0]
			except:
				admissions_bucket = None
			try:
				acceptance_rate = to_int(contents(admissions_bucket, [1, 0, 0, 1]).text)
			except:
				acceptance_rate = -1
			try:
				admissions_bucket = contents(admissions_bucket, [3, 0])
			except:
				admissions_bucket = None
			try:
				sat_range = contents(admissions_bucket, [0, 1]).text.split("-")
				sat_min = to_int(sat_range[0])
				sat_max = to_int(sat_range[1])
			except:
				sat_min = -1
				sat_max = -1
			try:
				application_fee = to_int(contents(admissions_bucket, [2, 1]).text)
			except:
				application_fee = -1
			try:
				sat_consideration = contents(admissions_bucket, [3, 1]).text
			except:
				sat_consideration = None
			try:
				gpa_consideration = contents(admissions_bucket, [4, 1]).text
			except:
				gpa_consideration = None
			has_early_decision = [i for i in soup.find_all(
				"div", "scalar--three") if "Early Decision" in i.text]
			accepts_common_app = [i for i in soup.find_all(
				"div", "scalar--three") if "Accepts Common App" in i.text]
			try:
				has_early_decision = contents(has_early_decision[0], [1]).text == "Yes"
			except:
				has_early_decision = False
			try:
				accepts_common_app = contents(accepts_common_app[0], [1]).text == "Yes"
			except:
				accepts_common_app = False
		my_sat = 1420
		sat_in_range = sat_min <= my_sat <= sat_max
		sat_at_least_min = my_sat >= sat_min
		try:
			cost_bucket = [i for i in soup.find_all(
				"div", "profile__buckets") if "Students Receiving Financial Aid" in i.text][0]
		except:
			cost_bucket = None
		price = to_int(contents(cost_bucket, [0, 0, 0, 1]).text.split(
			"/")[0][:-1]) if cost_bucket != None else -1
		cost_bucket = contents(cost_bucket, [1, 0]) if cost_bucket != None else None

		try:
			avg_aid = to_int(contents((cost_bucket), [0, 1, 0]).text)
		except:
			avg_aid = -1
		try:
			percent_receiving_aid = to_int(contents(cost_bucket, [1, 1]).text)
		except:
			percent_receiving_aid = -1
		try:
			student_faculty_ratio = [i for i in soup.find_all(
				"div", "scalar--three") if "Student Faculty Ratio" in i.text][0]
			student_faculty_ratio = str(contents(student_faculty_ratio, [1]).text)
		except:
			student_faculty_ratio = None
		try:
			percent_live_on_campus = [i for i in soup.find_all(
				"div", "scalar") if "Freshmen Live On-Campus" in i.text][0]
			percent_live_on_campus = to_int(contents(percent_live_on_campus, [1]).text)
		except:
			percent_live_on_campus = -1
		grad_bucket = [i for i in soup.find_all(
			"div", "profile__buckets") if "Employed 2 Years After Graduation" in i.text][0]
		try:
			earnings_6_yrs_after = to_int(contents(grad_bucket, [0, 0, 0, 1, 0]).text)
		except:
			earnings_6_yrs_after = -1
		try:
			job_confidence = to_int(contents(grad_bucket, [2, 0, 0, 0, 0]).text)
		except:
			job_confidence = -1
		try:
			job_confidence_responses = to_int(
				contents(grad_bucket, [2, 0, 0, 0, 1]).text)
		except:
			job_confidence_responses = -1
		grad_bucket = contents(grad_bucket, [1, 0])
		graduation_rate = to_int(contents(grad_bucket, [0, 1]))
		employed_2_yrs_after = to_int(contents(grad_bucket, [1, 1]))
		review_bucket = [i for i in soup.find_all(
			"div", "profile__buckets") if "Start Your Review" in i.text][0]
		num_of_reviews = to_int(contents(review_bucket, [0, 0, 0, 1, 2]).text)
		star_rating = round(
			float(contents(soup.find("div", "review__stars"), [1]).text.split(" ")[1]), 1)
		five_star_percent = to_int(
			contents(review_bucket, [1, 0, 0, 0, 0, 1, 0]).text)
		four_star_percent = to_int(
			contents(review_bucket, [1, 0, 0, 1, 0, 1, 0]).text)
		three_star_percent = to_int(
			contents(review_bucket, [1, 0, 0, 2, 0, 1, 0]).text)
		two_star_percent = to_int(
			contents(review_bucket, [1, 0, 0, 3, 0, 1, 0]).text)
		one_star_percent = to_int(
			contents(review_bucket, [1, 0, 0, 4, 0, 1, 0]).text)
		five_star_percent = round((five_star_percent/num_of_reviews)*100, 1)
		four_star_percent = round((four_star_percent/num_of_reviews)*100, 1)
		three_star_percent = round((three_star_percent/num_of_reviews)*100, 1)
		two_star_percent = round((two_star_percent/num_of_reviews)*100, 1)
		one_star_percent = round((one_star_percent/num_of_reviews)*100, 1)
		majors_link = link + "majors/"
		data_list = []
		data_list.append(str(name))
		data_list.append(str(niche_url_name))
		data_list.append(str(religious_affiliation))
		data_list.append(str(city))
		data_list.append(str(state))
		data_list.append(str(niche_grade))
		data_list.append(str(sat_consideration))
		data_list.append(str(gpa_consideration))
		data_list.append(str(first_descriptive_student_word))
		data_list.append(str(second_descriptive_student_word))
		data_list.append(str(third_descriptive_student_word))
		data_list.append(str(first_descriptive_college_word))
		data_list.append(str(second_descriptive_college_word))
		data_list.append(str(third_descriptive_college_word))
		data_list.append(str(academics_grade))
		data_list.append(str(value_grade))
		data_list.append(str(campus_grade))
		data_list.append(str(party_scene_grade))
		data_list.append(str(location_grade))
		data_list.append(str(campus_food_grade))
		data_list.append(str(safety_grade))
		data_list.append(str(professors_grade))
		data_list.append(str(dorms_grade))
		data_list.append(str(student_life_grade))
		data_list.append(str(price))
		data_list.append(str(student_num))
		data_list.append(str(comp_sci_student_num))
		data_list.append(str(city_size))
		data_list.append(str(comp_sci_rank))
		data_list.append(str(num_of_reviews))
		data_list.append(str(athletic_division))
		data_list.append(str(acceptance_rate))
		data_list.append(str(sat_min))
		data_list.append(str(sat_max))
		data_list.append(str(application_fee))
		data_list.append(str(percent_receiving_aid))
		data_list.append(str(avg_aid))
		data_list.append(str(student_faculty_ratio))
		data_list.append(str(descriptive_student_word_responses))
		data_list.append(str(diff_between_first_and_second_student_word))
		data_list.append(str(descriptive_college_word_responses))
		data_list.append(str(diff_between_first_and_second_college_word))
		data_list.append(str(percent_live_on_campus))
		data_list.append(str(graduation_rate))
		data_list.append(str(employed_2_yrs_after))
		data_list.append(str(earnings_6_yrs_after))
		data_list.append(str(job_confidence))
		data_list.append(str(job_confidence_responses))
		data_list.append(str(one_star_percent))
		data_list.append(str(two_star_percent))
		data_list.append(str(three_star_percent))
		data_list.append(str(four_star_percent))
		data_list.append(str(five_star_percent))
		data_list.append(str(star_rating))
		data_list.append(str(is_4_yr))
		data_list.append(str(has_early_decision))
		data_list.append(str(sat_in_range))
		data_list.append(str(sat_at_least_min))
		data_list.append(str(comp_sci_in_top))
		data_list.append(str(diversity_grade))
		data_list.append(str(athletics_grade))
		data_list.append(str(majors_link))
		data_list.append(str(description))
		data_list.append(str(short_name))
		data_list.append(str(all_women))
		data_list.append(str(accepts_common_app))
		data_list.append(str(is_online))
		data_list.append(str(min_major_num))
		with open("formatted_data.txt", "a") as f:
			f.write("<split>".join(data_list)+"\n")
	pbar.finish()

with open("formatted_data.txt", "r") as f:
	formatted_data = list(set(f.readlines()))
with open("formatted_data.txt", "w") as f:
	f.writelines(formatted_data)

if len(formatted_data) != 500:
	print("We got a problem")
	print(f"there are {len(formatted_data)} lines in the file")

print("\n\nDONE\n")
