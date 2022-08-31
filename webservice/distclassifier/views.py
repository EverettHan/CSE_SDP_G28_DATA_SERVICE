from datetime import datetime, timedelta
from django.http import HttpResponseBadRequest, HttpResponse, HttpRequest
from django.views import generic
from .models import *
from utilities.string_utils import is_null_or_empty
import json 
import time


# User Views -----------------------------------------------------------------------
class CreateUserView(generic.View):
    def post(self, request):
        # First check if username was supplied
        if "username" not in request.POST:
            return HttpResponseBadRequest("Username must be included")
        
        # Check if username is not null
        username = request.POST["username"]
        print(username)
        if is_null_or_empty(username):
            return HttpResponseBadRequest("Username can not be null")

        # Check if username is in use
        try:
            user = User.objects.get(username=username)
            user_already_exists_response = HttpResponse("user already exists")
            user_already_exists_response.status_code = 400
            return user_already_exists_response
        except Exception as e:
            # Create and save the current user
            User(username=username).save()
            return HttpResponse()

class GetAllUsersView(generic.View):
    def get(self, request):
        all_users = User.objects.all()
        comma_separated_usernames = []
        for user in all_users:
            comma_separated_usernames.append(user.username)
        return HttpResponse(str(comma_separated_usernames))

# Dataset Views -----------------------------------------------------------------------
class CreateDatasetView(generic.View):
    def post(self, request):
        # Check all necessary fields in the post request
        if not Dataset.is_valid(request.POST):
            return HttpResponseBadRequest()
        
        # Check to make sure this dataset has not been created before
        previous_dataset = None
        try:
            previous_dataset = Dataset.objects.get(name=request.POST["name"])
            return HttpResponseBadRequest("dataset name already in use")
        except:
            # There has not been a dataset object created using this dataset name
            pass

        Dataset.from_post(request.POST).save()
        return HttpResponse()

# ClassificationRequest Views -----------------------------------------------------------------------

class ClassifyView(generic.View):
    def post(self, request: HttpRequest):
        image = request.FILES['image']
        cr = ClassificationRequest(image=image)
        cr.requested_on = datetime.now()
        cr.save()
        
        count = 0
        messageReturn = "{ \"covidPred\": -1" + " }"
        while count < 60 :
            c_result = ClassificationResult.objects.filter(compute_request=cr)
            if c_result.count() != 0 :
                print ("found result")
                print (c_result[0].classification)
                messageReturn = c_result[0].classification
                break            
            time.sleep(1)
            count = count + 1          
        

        response = HttpResponse(messageReturn)
        response['Access-Control-Allow-Origin'] = '*'
        return response

class RequestWork(generic.View):
    def post(self, request: HttpRequest):
        # Get unassigned requests and requests with assigned dates older than three days
        assigned_on_threshold = (datetime.now() - timedelta(days=3)).isoformat()
        cr = ClassificationRequest.objects.filter(
            fulfilled=False, assigned_on__lte=assigned_on_threshold
        ).order_by('requested_on')
        if cr.count() == 0:
            return HttpResponse(json.dumps({'classification_id': None}))
        else:
            cr: ClassificationRequest = cr[0]
            now = datetime.now()
            cr.assigned_on = now
            cr.save()
            return HttpResponse(json.dumps({'classification_id': cr.pk, 'assigned_on': now.isoformat()}), content_type="application/json")

class RequestJobs(generic.View):
    def post(self, request: HttpRequest):
        # Get unassigned requests and requests with assigned dates older than three days
        assigned_on_threshold = (datetime.now() - timedelta(days=3)).isoformat()
        c_reqs = ClassificationRequest.objects.filter(
            fulfilled=False, assigned_on__lte=assigned_on_threshold
        ).order_by('requested_on')

        jobList = []
        if c_reqs.count() == 0:
            return HttpResponse(json.dumps(jobList))
        else:
            jobCount = 0
            for c_req in c_reqs:
                now = datetime.now()
                c_req.assigned_on = now
                c_req.save()
                job = {'classification_id': c_req.pk, 'assigned_on': now.isoformat()}
                jobList.append(job)
                jobCount += 1
                if jobCount >= 10:
                    break
            
            return HttpResponse(json.dumps(jobList), content_type="application/json")

class GetImage(generic.View):
    def get(self, request: HttpRequest):
        cr_pk = request.GET['classification_id']
        cr = ClassificationRequest.objects.get(pk=cr_pk)
        response = HttpResponse(cr.image, content_type="image")
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(cr.image.name)
        return response

class ReportClassification(generic.View):
    def post(self, request: HttpRequest):
        b = json.loads(request.body)
        cr = ClassificationRequest.objects.filter(
            fulfilled = False, assigned_on = datetime.fromisoformat(b['assigned_on']), pk = b['classification_id']
        )
        if cr.count() == 0:
            return HttpResponse("Request has either already been fulfilled or does not exist", status=404)
        cr: ClassificationRequest = cr[0]
        cr.fulfilled = True
        c_result = ClassificationResult(classification=b['classification'], compute_request=cr, completed_on=datetime.now(), errors=b['errors'])
        c_result.save()
        cr.save()
        return HttpResponse()


# ClassificationRequest Views -----------------------------------------------------------------------

# Create a ClassificationRequest model instance
def ClassificationRequestFormCreateView(request):
    # Handle file upload
    if request.method == 'POST':
        form = ClassificationRequestForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # FUNCTION TO DO UPLOAD IMAGE TO S3
            S3_service = AWS_S3.S3()
            S3_service.upload_file(form.cleaned_data['image'], "sdps3testbucket")
            return HttpResponse(status=201)
    else:
        #form = ClassificationRequestForm()
        mimeType = request.GET.get('mimeType', '')
        objectKey = request.GET.get('objectKey', '')
        bucketName = request.GET.get('bucketName', '')
        filePath = 'd:\\temp\\team28.'
        if mimeType == 'image/jpeg':
            filePath += 'jpg'
        elif mimeType == 'image/png':
            filePath += 'png'
        else:
            assert True
        print ("aaaa")
        print (mimeType+objectKey+bucketName)    

        #downfileFromS3('1616119765495-team-28-48216912-beach-ball-.jpg', 'binarystorage1', filePath)
        downfileFromS3(objectKey, bucketName, filePath)
        #downfileFromS3('1616119765495-team-28-48216912-beach-ball-.jpg', 'binarystorage1', 'd:\\temp\\team28.jpg')
        return HttpResponse("hello world, done")

# ClassificationResult Views -----------------------------------------------------------------------


class GetResults(generic.View):
    def get(self,request):
        # First check to see if there is a corresponding classification request
        classification_id = request.GET['classification_id']
        cr = ClassificationRequest.objects.filter(pk=classification_id)
        if cr.count() == 0:
            return HttpResponse("No classification request with id: {}".format(classification_id), status=404)
        
        cr = cr[0] # Get the actual request

        # Then check to see if that classification request has a result
        # Regardless if there's a result or not we can determine if the request has been assigned to a
        # Worker or not
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = '*'
        c_result = ClassificationResult.objects.filter(compute_request=cr)
        if c_result.count() == 0:
            response.content = json.dumps({'classification': "Request has not yet been fulfilled."})
        else:
            response.content = c_result[0].to_json()
            
        return response
