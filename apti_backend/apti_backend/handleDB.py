from re import X
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def get_all_questions():
	questions = db.collection("ques_bank").stream()
	data = []

	for q in questions:
		_id = q.id
		doc = q.to_dict()
		doc["id"] = _id
		data.append(doc)

	data.sort(key = lambda x:x['no'])
	return data

def add_analytics_to_user(email, level, topics):
	"""
	level =
	{
		"os": {
			"hard": [3, 2, 1],
			"medium": [3, 1, 2],
			"easy": [3, 3, 0]
		},
		"dbms": {
			"hard": [3, 1, 2],
			"medium": [3, 1, 2],
			"easy": [3, 2, 1]
		},
		"dsa": {
			"hard": [3, 3, 0],
			"medium": [3, 2, 1],
			"easy": [3, 2, 1]
		},
		"cn": {
			"hard": [3, 0, 3],
			"medium": [3, 1, 2],
			"easy": [3, 2, 1]
		},
		"quants": {
			"hard": [3, 2, 1],
			"medium": [3, 3, 0],
			"easy": [3, 1, 2]
		}
	}
	"""
	users = db.collection("user").where(u'email', u'==', email).get()

	if len(users) > 0:
		uid = users[0].id
		db.collection("user").document(uid).update({
			"level_wise": level,
			"topic_wise": topics
		})

	return True


def get_user_data(email):
	users = db.collection("user").where(u'email', u'==', email).get()

	if len(users) > 0:
		uid = users[0].id
		udata = users[0].to_dict()
		return {uid : udata}

	return None

def get_global_ranklist():
	users_ref = db.collection(u'user')
	query = users_ref.order_by(
    u'total_score', direction=firestore.Query.DESCENDING).get()

	lst=[]
	for doc in query:
		data = doc.to_dict()
		lst.append(data)

	# n=len(lst)

	# for i in range(0,n):
	# 	str=""
	# 	rank="{}".format(i+1)
	# 	str+=rank
	# 	total_score="{}".format(lst[i]['total_score'])
	# 	str+=" "
	# 	str+=(lst[i]['name'])
	# 	str+=" "
	# 	str+=total_score
	# 	str+=" "
	# 	str+=(lst[i]['college'])
	# 	print(str)

	return lst


def get_college_ranklist(college):
	users_ref = db.collection(u'user')
	query = users_ref.order_by(
    u'total_score', direction=firestore.Query.DESCENDING).get()

	lst=[]
	x = 1
	for doc in query:
		data = doc.to_dict()
		if(data['college']=="Shri Ramdeobaba College of Engineering and Management"):
			dict = {
				"rank": x,
				"name":data['name'],
				"marks":data['total_score'],
			}
			lst.append(dict)
			x=x+1

	# n=len(lst)

	# for i in range(0,n):
	# 	str=""
	# 	rank="{}".format(i+1)
	# 	str+=rank
	# 	total_score="{}".format(lst[i]['total_score'])
	# 	str+=" "
	# 	str+=(lst[i]['name'])
	# 	str+=" "
	# 	str+=total_score
	# 	str+=" "
	# 	str+=(lst[i]['college'])
	# 	print(str)

	return lst

# {
# 	"college":  "Shri Ramdeobaba College of Engineering and Management"
# }