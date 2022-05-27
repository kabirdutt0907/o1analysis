from os import stat
from django.http import HttpResponse, JsonResponse

from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
import requests

from .handleDB import *
from .serializers import *


@api_view(['POST'])
def register(request):
	"""
	{
		"name": "Demo User8",
		"email": "demouser8@gmail.com",
		"college": "Yeshwantrao Chavan College of Engineering",
		"key": "YCCE",
		"mobile": 8888888888
	}
	"""
	serializer = UserSerializer(data=request.data)

	if serializer.is_valid():
		data = serializer.data
		college = data['college']
		key = data['key']

		user_data = {
			'name': data['name'],
			'email': data['email'],
			'college': data['college'],
			'mobile': data['mobile'],
		}

		user_id = data["email"].split("@")[0]

		if check_id_exist(user_id)!=0:
			print("EMAIL ALREADY EXIST")
			return Response("EMAIL ALREADY EXIST", status=status.HTTP_400_BAD_REQUEST)

		if check_college_exist(college)!=1:
			print("COLLEGE DOES NOT EXIST")
			return Response("COLLEGE DOES NOT EXIST", status=status.HTTP_400_BAD_REQUEST)

		collegekey = get_college_key(college)

		if (collegekey==-1):
			print("KEY FINDING ERROR")
			return Response("KEY FINDING ERROR", status=status.HTTP_401_UNAUTHORIZED)

		if (key==collegekey):
			print("MATCHED")
			create_user(user_data, user_id)
			return Response("REGISTERED SUCCESSFULLY", status=status.HTTP_201_CREATED)
		else:
			print("NOT MATCHED")
			return Response("WRONG KEY", status=status.HTTP_401_UNAUTHORIZED)

	else:
		return Response("INVALID DATA", status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
	"""
	{
		"email": "demouser8@gmail.com",
		"college": "Yeshwantrao Chavan College of Engineering",
		"key": "YCCE"
	}
	"""
	serializer = UserLoginSerializer(data=request.data)

	if serializer.is_valid():
		data = serializer.data

		email = data['email']
		college = data['college']
		key = data['key']

		dict = {
			'email': email,
			'college': college,
			'key': key,
		}

		user_id = email.split("@")[0]

		if (check_id_exist(user_id)!=1):
			print("EMAIL DOES NOT EXIST")
			return Response("EMAIL DOES NOT EXIST", status=status.HTTP_401_UNAUTHORIZED)

		clg = get_college_name(user_id)

		if (clg==0 or clg==-1):
			print("WRONG COLLEGE NAME")
			return Response("WRONG COLLEGE NAME", status=status.HTTP_401_UNAUTHORIZED)

		if (clg!=college):
			print("WRONG COLLEGE NAME")
			return Response("WRONG COLLEGE NAME", status=status.HTTP_401_UNAUTHORIZED)

		collegekey = get_college_key(college)

		if(collegekey==-1):
			print("KEY FINDING ERROR")
			return Response("KEY FINDING ERROR", status=status.HTTP_401_UNAUTHORIZED)

		if(key==collegekey):
			print("LOGGED IN SUCCESFULLY")
			return Response("LOGGED IN SUCCESSFULLY", status=status.HTTP_200_OK)
		else:
			print("NOT MATCHED")
			return Response("WRONG key", status=status.HTTP_401_UNAUTHORIZED)

	else:
		return Response("INVALID DATA", status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def ranklist(request):
	"""
	{
		"college" : "Shri Ramdeobaba College of Engineering and Management"
	}
	"""
	serializer = CollegeRankListSerializer(data = request.data)
	if serializer.is_valid():
		college = serializer.data['college']
		lst = get_college_ranklist(college)
		data = {
			"ranklist" : lst
		}
		return Response(data, status = status.HTTP_200_OK)

	return Response(status = status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def globalranklist(request):
	lst = get_global_ranklist()
	data = {
		"ranklist" : lst
	}
	return Response(data, status = status.HTTP_200_OK)


@api_view(['GET'])
def question_bank(request):
	questions = get_all_questions()
	return Response({"data" : questions}, status = status.HTTP_200_OK)


@api_view(['POST'])
def analytics(request):
	"""
	{
		"email": "demouser8@gmail.com"
	}
	"""
	serializer = EmailSerializer(data = request.data)
	if serializer.is_valid():
		email = serializer.data['email']
		data = get_user_data(email)

		if data is None:
			return Response("No user found", status = status.HTTP_404_NOT_FOUND)

		return Response(data, status = status.HTTP_200_OK)
	else:
		return Response("Invalid data", status = status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def get_test_analysis(request):
	"""
	{
		"email": "demouser7@gmail.com",
		"subject_frontend":"overall"
	}
    """
	serializer = analysisSerializer(data = request.data)
	if(serializer.is_valid()) :
		email=serializer.data['email']
		subject_frontend=serializer.data['subject_frontend']
	answers_temp=get_user_answers()
	u_id=""
	for str in email:
		if(str=='@'):
			break;
		else:
			u_id=u_id+str
	#email=u_id+"@gmail.com"
	data=get_user_data(email)
	status=0
	if('status' in data):
		status=data['status']
	else:
		status=0
	#print(data['Status'])
    

	#### DB Fields
	totaldb=0
	scores={}
	level_wise_distribution={}
	topic_wise_distribution={}
	plus=0


	if(status==0):
		status=1
		Questions = get_all_questions()
		for question in Questions:
			#print(question.to_dict())
			#question=quest.to_dict()
			no=question['no']
			topic=question['subject']
			subtopic=question['topic']
			corr=question['answer']
			diff=question['level']

			#### Fields check
			if not topic in scores:
				scores[topic]=0
			if not topic in level_wise_distribution:
				level_wise_distribution[topic]={
							"hard":[0,0,0],
							"medium":[0,0,0],
							"easy":[0,0,0]
						}
			if not topic in topic_wise_distribution:
				topic_wise_distribution[topic]={}
			if not topic in topic_wise_distribution[topic]:
				topic_wise_distribution[topic][subtopic]=[0,0,0]
    
    
			#### correct then
			if(answers_temp[no]==corr):
				# Update data with known key
				#db.collection('persons').document("p1").update({"age": 50}) # field already exists
				#db.collection('persons').document("p1").update({"age": firestore.Increment(2)}) # increment a field

				if(diff=='easy'):
					plus=2

				if(diff=='medium'):
					plus=4

				if(diff=='hard'):
					plus=6

				level_wise_distribution[topic]['easy'][1]=level_wise_distribution[topic][diff][1]+1
				topic_wise_distribution[topic][subtopic][1]=topic_wise_distribution[topic][subtopic][1]+1
				totaldb=totaldb+plus
				scores[topic]=scores[topic]+plus
				level_wise_distribution[topic]['easy'][0]=level_wise_distribution[topic]['hard'][0]+plus
				topic_wise_distribution[topic][subtopic][0]=topic_wise_distribution[topic][subtopic][0]+plus


			else:
				level_wise_distribution[topic]['easy'][2]=level_wise_distribution[topic][diff][2]+1
				topic_wise_distribution[topic][subtopic][2]=topic_wise_distribution[topic][subtopic][2]+1

		update_scored_db(totaldb,scores,level_wise_distribution,topic_wise_distribution,status,u_id)

	else:
		print("alredy exist")
    
	############# RETURNING JSON RESPONSE ///// ANALYSIS DATA
 
 
	subject=subject_frontend
	data1=get_user_data(email)
	namer=data1['name']
	scores_subject=[]
	subject1=[]
	correct=[]
	incorrect=[]
	hard=0
	medium=0
	easy=0
	total=0
        
	if(subject=='overall'):
		
		total=data1['total_score']
		for sub in data1['level_wise_distribution']:
			innerdata=data1['level_wise_distribution'][sub]
			subject1.append(sub)
			hard=hard+innerdata['hard'][0]
			medium=medium+innerdata['medium'][0]
			easy=easy+innerdata['easy'][0]
			correct.append(innerdata['hard'][1]+innerdata['medium'][1]+innerdata['easy'][1])
			incorrect.append(innerdata['hard'][2]+innerdata['medium'][2]+innerdata['easy'][2])
			scores_subject.append(data1['scores'][sub])

	else:
		hard=data1['level_wise_distribution'][subject]['hard'][0]
		medium=data1['level_wise_distribution'][subject]['medium'][0]
		easy=data1['level_wise_distribution'][subject]['easy'][0]
		total=hard+easy+medium
		for topic in data1['topic_wise_distribution'][subject]:
			subject1.append(topic)
			innerdata=data1['topic_wise_distribution'][subject][topic]
			correct.append(innerdata[1])
			incorrect.append(innerdata[2])
			scores_subject.append(innerdata[0])



	returndata={
				'name': namer,
				'total': total,
				'leetcode': {
				'series': [hard, medium, easy],
				'labels': ["Hard", "Medium", "Easy"],
				},
				'stackgraph': {
				'series': [
					{
					'name': "Correct",
					'data': correct,
					},
					{
					'name': "Incorrect",
					'data': incorrect,
					},
				],
				'labels': subject1,
				},
				'linegraph': {
				'labels': subject1,
				'series': [
					{
					'name': "Subjects",
					'data': scores_subject,
					},
				],
				},
				'piechart': {
				'series': scores_subject,
				'labels': subject1,
				},
			}
    
	return Response(returndata)


@api_view(['POST'])
def fetch_user_responses(request):
	"""
	{
		"email" : "riteshjaiswal01234@gmail.com"
	}
	"""
	serializer = EmailSerializer(data = request.data)
	if serializer.is_valid():
		data = serializer.data
		user_responses = get_user_responses(data['email'])
		return Response(user_responses, status = status.HTTP_200_OK)

@api_view(['GET'])
def college_list(request):
    clg_listdb = db.collection('college').get()
    clg_list=[]
    for c in clg_listdb:
        c=c.to_dict()
        clg_list.append(c['college_name'])
    clg_list=sorted(clg_list)
    clg_dict={"clg_names":clg_list}
    #returning dict to json
    # json_object = json.dumps(clg_dict, indent = 4) 
    return Response(clg_dict , status = status.HTTP_200_OK)


@api_view(['POST'])
def weakest_topics(request):
    """
	{
		"email" : "demouser7@gmail.com"
	}
	"""
    serializer = EmailSerializer(data = request.data)
    if serializer.is_valid():
        ser_data = serializer.data
        email = ser_data['email']
        user_id = email.split("@")[0]
        
        if check_id_exist(user_id)!=1:
            print("EMAIL DOES NOT EXIST")
            return Response("EMAIL DOES NOT EXIST", status=status.HTTP_400_BAD_REQUEST)
        
        user_data=get_user_data(email)
        
        subjects=user_data["topic_wise_distribution"]
    
        subject_list=[]
        topic_list=[]
        
        for subject in subjects.keys():
            
            subject_list.append(subject)            
            topics=subjects[subject]
            
            var=999999
            weak_topic=""
            
            for topic in topics.keys():
                mark=topics[topic][0]
                if(mark<var):
                    var=mark
                    weak_topic=topic
            
            topic_list.append(weak_topic)
            
        print(subject_list)
        print(topic_list)  
        
        dict={}
        
        sz=len(subject_list)
        
        for i in range(0,sz):
            dict.update({subject_list[i]:topic_list[i]})
            
        return Response(dict, status = status.HTTP_200_OK)
    
    return Response("INVALID DATA (ISSUE IN SERIALIZATION)", status = status.HTTP_400_BAD_REQUEST)
        
        
        