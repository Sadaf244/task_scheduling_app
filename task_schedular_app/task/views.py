from rest_framework.views import APIView
from django.http import JsonResponse
import logging
from accounts.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from task.models import CreateTaskManager,GetTaskManager, GetAllTaskManager,DeleteTaskManager,UpdateTaskManager


class CreateTask(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        resp_dict = dict()
        resp_dict['status'] = False
        resp_dict['message'] = "Something went wrong. Please try again after sometime"
        try:
            user = request.user
            create_task_manager = CreateTaskManager(user, request)
            save_task_resp = create_task_manager.save_user_task()
            resp_dict['status'] = save_task_resp['status']
            resp_dict['message'] = save_task_resp['message']
        except Exception as e:
            logging.error('getting exception on CreateTask', repr(e))
        return JsonResponse(resp_dict, status=200)


class GetTask(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request, task_id):
        resp_dict = dict()
        resp_dict['status'] = False
        resp_dict['message'] = "Something went wrong. Please try again after sometime"
        try:
            user = request.user
            print(user)
            get_task_manager = GetTaskManager(user, task_id)
            get_task_manager_resp = get_task_manager.get_user_task()
            resp_dict['data'] = get_task_manager_resp['data']
            resp_dict['status'] = get_task_manager_resp['status']
            resp_dict['message'] = get_task_manager_resp['message']
        except Exception as e:
            logging.error('getting exception on GetTask', repr(e))
        return JsonResponse(resp_dict, status=200)


class GetAllTask(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        resp_dict = dict()
        resp_dict['status'] = False
        resp_dict['message'] = "Something went wrong. Please try again after sometime"
        try:
            user = request.user
            get_all_task_manager = GetAllTaskManager(user)
            get_task_manager_resp = get_all_task_manager.get_user_task_list()
            resp_dict['data'] = get_task_manager_resp['data']
            resp_dict['status'] = get_task_manager_resp['status']
            resp_dict['message'] = get_task_manager_resp['message']
        except Exception as e:
            logging.error('getting exception on GetAllTask', repr(e))
        return JsonResponse(resp_dict, status=200)


class DeleteTask(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def delete(self, request, task_id):
        resp_dict = dict()
        resp_dict['status'] = False
        resp_dict['message'] = "Something went wrong. Please try again after sometime"
        try:
            user = request.user
            delete_task_manager = DeleteTaskManager(user, task_id)
            delete_task_manager_resp = delete_task_manager.delete_user_task()
            resp_dict['data'] = delete_task_manager_resp['data']
            resp_dict['status'] = delete_task_manager_resp['status']
            resp_dict['message'] = delete_task_manager_resp['message']
        except Exception as e:
            logging.error('getting exception on DeleteTask', repr(e))
        return JsonResponse(resp_dict, status=200)


class UpdateTask(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def put(self, request, task_id):
        resp_dict = dict()
        resp_dict['status'] = False
        resp_dict['message'] = "Something went wrong. Please try again after sometime"
        try:
            user = request.user
            update_task_manager = UpdateTaskManager(user, task_id, request)
            update_task_manager_resp = update_task_manager.update_user_task()
            resp_dict['data'] = update_task_manager_resp['data']
            resp_dict['status'] = update_task_manager_resp['status']
            resp_dict['message'] = update_task_manager_resp['message']
        except Exception as e:
            logging.error('getting exception on UpdateTask', repr(e))
        return JsonResponse(resp_dict, status=200)