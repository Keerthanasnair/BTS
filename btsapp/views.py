from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.contrib import messages
from django.db.models import *
from .models import *
import re
import subprocess

#from transformers import BartTokenizer, BartForSequenceClassification
from transformers import pipeline
from datetime import datetime


@never_cache
def login_page(request):
    return render(request, "login.html")


@csrf_exempt
@never_cache
def login(request):
    email = request.POST.get("email")
    password = request.POST.get("password")
    print(f"{email} {password}")
    data = {}

    # ob_mail = User.objects.get(email=email)
    # print(f'login check->{ob_mail}')
    if email == "admin@gmail.com" and password == "admin":
        request.session["mail"] = email
        data["result"] = "A"
        return JsonResponse(data, safe=False)
        # return render(request, 'home.html')
    elif User.objects.filter(email=email, password=password).exists():
        ob_mail = User.objects.get(email=email)
        user_role = ob_mail.role
        if user_role == "developer":
            request.session["mail"] = email
            data["result"] = "D"
            return JsonResponse(data, safe=False)
        else:
            request.session["mail"] = email
            data["result"] = "T"
            return JsonResponse(data, safe=False)
    else:
        data["result"] = "N"
        return JsonResponse(data, safe=False)


def logout(request):
    if "mail" in request.session:
        del request.session["mail"]
    return render(request, "login.html")


@csrf_exempt
@never_cache
def register(request):
    name = request.POST.get("username")
    email = request.POST.get("mail")
    password = request.POST.get("password")
    role = request.POST.get("role")
    print(f"Name: {name}, Mail: {email}, Password: {password}, Role: {role}")

    data = {}
    reg_p1 = User.objects.filter(email=email)
    if reg_p1.count() > 0:
        data["result"] = "no"
        return HttpResponse("<script>alert('Email already Exist);</script>")
    else:
        reg_p2 = User(username=name, email=email, password=password, role=role)
        reg_p2.save()

        data["result"] = "yes"
        print("Response data: ", data)
        saved_User = User.objects.get(pk=reg_p2.pk)
        print(
            f"Name: {saved_User.username}, Mail: {saved_User.email}, Password: {saved_User.password}, Role: {saved_User.role}"
        )
        return JsonResponse(data, safe=False)


def admin_home(request):
    total_tasks = Scripts.objects.count()
    unassigned_tasks = Scripts.objects.filter(status="received").count()
    pending_tasks = Tasks.objects.filter(status="in progress").count()
    completed_tasks = Tasks.objects.filter(
        Q(status="test done") | Q(status="test failed")
    ).count()
    active_testers = User.objects.filter(role="tester").count()
    unread_count = Notification.objects.filter(is_read=False).count()
    print("Notification count -> ", unread_count)
    context = {
        "total_tasks": total_tasks,
        "unassigned_tasks.": unassigned_tasks,
        "pending_tasks": pending_tasks,
        "completed_tasks": completed_tasks,
        "active_testers": active_testers,
        "unread_count": unread_count,
    }
    return render(request, "admin_home.html", context)


@csrf_exempt
def chat_page(request):
    return render(request, "chat.html")


@csrf_exempt
def chat(request):
    if request.method == "POST":
        user_message = request.POST.get("message")
        if user_message:
            bot_response = chatbot.get_response(user_message)
            # bot_response = 'kkk'
            return JsonResponse({"response": str(bot_response)})
        else:
            return JsonResponse({"response": "No message received."})
    return render(request, "chat.html")


def developer_home(request):
    if "mail" in request.session:
        email = request.session["mail"]
        user_ob = User.objects.get(email=email)
        username = user_ob.username
        total_scripts = Scripts.objects.filter(devid=user_ob).count()

        # Query the number of scripts pending review
        pending_scripts = Tasks.objects.filter(
            script_from=username, status="sent"
        ).count()

        # Query the number of scripts in progress
        in_progress_scripts = Tasks.objects.filter(
            script_from=username, status="in progress"
        ).count()

        # Query the number of completed scripts
        completed_scripts = Tasks.objects.filter(
            script_from=username, status="test done"
        ).count()
        context = {
            "username": username,
            "total_scripts": total_scripts,
            "pending_scripts": pending_scripts,
            "in_progress_scripts": in_progress_scripts,
            "completed_scripts": completed_scripts,
        }
    return render(request, "developer_home.html", context)


def developer_submit_website_page(request):
    return render(request, "developer_submit_website_page.html")


def tester_home(request):
    if "mail" in request.session:
        email = request.session["mail"]
        user_ob = User.objects.get(email=email)
        username = user_ob.username
        print(username)
        uid = user_ob.userid
        total_assigned_scripts = Tasks.objects.filter(assign_to=username).count()
        in_progress_scripts = Tasks.objects.filter(
            assign_to=username, status="in progress"
        ).count()
        # completed_reports = Tasks.objects.filter(assign_to=username, status='test done').count()
        completed_reports = Report.objects.filter(created_by=username).count()

        print(total_assigned_scripts, in_progress_scripts, completed_reports)

    return render(
        request,
        "tester_home.html",
        {
            "username": username,
            "total_assigned_scripts": total_assigned_scripts,
            "in_progress_scripts": in_progress_scripts,
            "completed_reports": completed_reports,
        },
    )


def check_tasks(request):
    scripts = Scripts.objects.all()
    testers = User.objects.filter(role="tester")
    websites = Website.objects.all()

    context = {
        "scripts": scripts,
        "websites": websites,
        "testers": testers,
    }
    return render(request, "check_tasks.html", context)


def users_list(request):
    users = User.objects.all()
    return render(request, "users_list.html", {"users": users})


@csrf_exempt
def edit_user(request):
    id = request.POST.get("uid")
    name = request.POST.get("name")
    email = request.POST.get("email")
    password = request.POST.get("password")
    role = request.POST.get("role")
    print(f"id:{id}, Userame: {name}, Mail: {email}, PSWD: {password}, Role: {role}")

    data = {}

    edit_ob1 = User.objects.get(userid=int(id))

    edit_ob1.username = name
    edit_ob1.email = email
    edit_ob1.password = password
    edit_ob1.role = role
    print(
        f"id:{id}, Userame: { edit_ob1.username}, Mail: { edit_ob1.email}, PSWD: { edit_ob1.password}, Rolee: { edit_ob1.role}"
    )

    edit_ob1.save()
    data["msg"] = "Successfully Updated!!.."
    return JsonResponse(data, safe=False)
    return HttpResponse(
        "<script>alert('Successfully Updated!!..');window.location.href='/users_list/'</script>"
    )


@csrf_exempt
def delete_user(request):
    userid = request.POST.get("id")
    print(userid)
    data = {}
    delete_user = User.objects.get(userid=int(userid))
    if delete_user:
        delete_user.delete()
        data["msg"] = "Data Deleted Successfully!.."
        return JsonResponse(data, safe=False)
    # return HttpResponse("<script>alert('Data Deleted Successfully!..');window.location.href='/users_list/'</script>")


def task_assign(request):
    reports = Report.objects.all()
    websitereports = WebsiteReport.objects.all()
    return render(request, "task_assign.html", {"reports": reports, "websitereports": websitereports})


def total_task(request):
    scripts = Scripts.objects.all()
    websites = Website.objects.all()

    context = {
        "scripts": scripts,
        "websites": websites,
        
    }
    return render(request, "total_tasks.html", context)


def pending_task(request):
    pending_tasks = Tasks.objects.filter(status="in progress")
    website_pending_tasks = WebsiteTasks.objects.filter(status="in progress")
    context = {
        "tasks": pending_tasks,
        "website_tasks": website_pending_tasks,
    }
    return render(request, "pending_tasks.html", context)


def completed_task(request):
    completed_tasks = Tasks.objects.filter(
        Q(status="test done") | Q(status="test failed")
    )
    
    website_completed_tasks = WebsiteTasks.objects.filter(
        Q(status="test done") | Q(status="test failed")
    )
    context = {
        "tasks": completed_tasks,
        "website_tasks": website_completed_tasks,
    }
    return render(request, "completed_tasks.html", context)


def dev_total(request):
    if "mail" in request.session:
        mail = request.session["mail"]
        usr_obj = User.objects.get(email=mail)
        scripts = Scripts.objects.filter(devid=usr_obj)
        websites = Website.objects.filter(devid=usr_obj)

        context = {
            "scripts": scripts,
            "websites": websites,
        }
        return render(request, "dev_total.html", context)


def dev_pending(request):
    if "mail" in request.session:
        mail = request.session["mail"]
        usr_obj = User.objects.get(email=mail)
        pending_tasks = Tasks.objects.filter(
            status="in progress", script_from=usr_obj.username
        )
        
        website_pending_tasks = WebsiteTasks.objects.filter(
            status="in progress", website_from=usr_obj.username
        )
        context = {
            "tasks": pending_tasks,
            "website_tasks": website_pending_tasks,
        }
        return render(request, "dev_pending.html", context)


def tester_total(request):
    if "mail" in request.session:
        mail = request.session["mail"]
        usr_obj = User.objects.get(email=mail)
        total_assigned = Tasks.objects.filter(assign_to=usr_obj.username)
        
        website_total_assigned = WebsiteTasks.objects.filter(
            assign_to=usr_obj.username
        )
        
        context = {
            "tasks": total_assigned,
            "website_tasks": website_total_assigned,
        }
        return render(request, "tester_total.html", context)


def tester_progress(request):
    if "mail" in request.session:
        mail = request.session["mail"]
        usr_obj = User.objects.get(email=mail)
        in_progress = Tasks.objects.filter(
            status="in progress", script_from=usr_obj.username
        )
        
        websites_in_progress = WebsiteTasks.objects.filter(
            status="in progress", website_from=usr_obj.username
        )
    
        
        context = {
            "tasks": in_progress,
            "website_tasks": websites_in_progress,
        }
        return render(request, "tester_progress.html", context)


def dev_pend_review(request):
    if "mail" in request.session:
        mail = request.session["mail"]
        usr_obj = User.objects.get(email=mail)
        pend_review = Tasks.objects.filter(status="sent", script_from=usr_obj.username)
        website_pend_review = WebsiteTasks.objects.filter(
            status="sent", website_from=usr_obj.username
        )
        context = {
            "tasks": pend_review,
            "website_tasks": website_pend_review,
        }
        return render(request, "dev_pend_review.html", context)


def dev_completed(request):
    if "mail" in request.session:
        mail = request.session["mail"]
        usr_obj = User.objects.get(email=mail)
        completed_tasks = Tasks.objects.filter(
            status="test done", script_from=usr_obj.username
        )
        
        website_tasks =  WebsiteTasks.objects.filter(
            status="test done", website_from=usr_obj.username
        )
        context = {
            "tasks": completed_tasks,
            "website_tasks": website_tasks,
        }
        return render(request, "dev_completed.html", context)


def dashboard_summary(request):
    return render(request, "dashboard_summary.html")


def upload_page(request):
    if "mail" in request.session:
        email = request.session["mail"]
        user_ob = User.objects.get(email=email)
        username = user_ob.username
        total_scripts = Scripts.objects.count()
        print("Total-> ", total_scripts)

        return render(
            request,
            "upload_script.html",
            {"username": username, "total_scripts": total_scripts},
        )


@csrf_exempt  # If using CSRF tokens, you don't need this decorator
def upload_script(request):
    email = request.session["mail"]
    obj = User.objects.get(email=email)
    uid = obj.userid
    dt = datetime.now()
    dt_string = dt.strftime("%Y-%m-%d %H:%M:%S")
    print(dt_string, " ", uid)
    if request.method == "POST":
        file = request.FILES.get("file")
        requirements = request.POST.get("requirements")
        if file:
            Scripts.objects.create(
                devid=obj,
                filename=file.name,
                upfile=file,
                created_date=dt_string,
                requirements=requirements,
                status="received",
                assigned_to="yet to assign",
            )
            Notification.objects.create(
                user_email=email,
                message=f"The {file.name} script has been uploaded by {obj.username} on {dt_string}.",
            )
            return JsonResponse(
                {"success": True, "message": "File uploaded successfully!"}
            )

        return JsonResponse({"success": False, "message": "No file provided!"})

    return JsonResponse({"success": False, "message": "Invalid request method!"})


@csrf_exempt
def developer_submit_website(request):
    if "mail" in request.session:
        email = request.session["mail"]

    user_obj = User.objects.get(email=email)
    user_id = user_obj.userid

    if request.method == "POST":
        website_url = request.POST.get("website_url")
        requirements = request.POST.get("website_requirements")
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if website_url:
            Website.objects.create(
                url=website_url,
                created_at=created_at,
                devid=user_obj,
                requirements=requirements,
                status="received",
                assigned_to="yet to assign",
            )
            print("Website created")

            Notification.objects.create(
                user_email=email,
                message=f"The {website_url} website has been submitted by {user_obj.username} on {created_at}.",
            )
            return JsonResponse(
                {"success": True, "message": "Website submitted successfully!"}
            )

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def assign_website(request):
    print("Assigning website")
    website_id = request.POST.get("website_id")
    assign_to = request.POST.get("tester_id")
    status = request.POST.get("status")
    print(f"Website ID: {website_id}, Assign to: {assign_to}, Status: {status}")
    website_obj = Website.objects.get(website_id=int(website_id))
    devid = website_obj.devid.userid
    usr_obj = User.objects.get(userid=int(devid))
    devname = usr_obj.username
    tester_obj = User.objects.get(userid=int(assign_to))
    testername = tester_obj.username
    dt = datetime.now()
    dt_string = dt.strftime("%Y-%m-%d %H:%M:%S")

    WebsiteTasks.objects.create(
        website=website_obj,
        assign_to=testername,
        website_from=devname,
        status=status,
        received_date=dt_string,
        requirements=website_obj.requirements,
    )

    website_obj.status = "sent"
    website_obj.assigned_to = testername
    website_obj.save()
    
    print("Website assigned")
    return JsonResponse({"success": True, "message": "Website assigned successfully!"})


def developer_view_status(request):
    reports = Report.objects.all()
    websiteReports = WebsiteReport.objects.all()
    return render(request, "developer_view_status.html", {"reports": reports, "websiteReports": websiteReports})


@csrf_exempt
def assigned_tasks(request):
    script = request.POST.get("script_id")
    assign = request.POST.get("tester_id")
    status = request.POST.get("status")
    script_obj = Scripts.objects.get(scriptid=int(script))
    devid = script_obj.devid.userid
    usr_obj = User.objects.get(userid=int(devid))
    devname = usr_obj.username
    tester_obj = User.objects.get(userid=int(assign))
    testername = tester_obj.username
    dt = datetime.now()
    dt_string = dt.strftime("%Y-%m-%d %H:%M:%S")

    Tasks.objects.create(
        script=script_obj,
        assign_to=testername,
        script_from=devname,
        status=status,
        received_date=dt_string,
        requirements=script_obj.requirements,
    )
    script_obj.status = "sent"
    script_obj.assigned_to = testername
    script_obj.save()

    return JsonResponse({"success": True, "message": "Task assigned successfully!"})


def tasks_page(request):
    if "mail" in request.session:
        mail = request.session["mail"]
        user = User.objects.get(email=mail)

        if user.role == "tester":
            tasks = Tasks.objects.filter(assign_to=user.username)
            web_tasks = WebsiteTasks.objects.filter(assign_to=user.username)
            return render(
                request,
                "tasks.html",
                {"tasks": tasks, "web_tasks": web_tasks, "username": user.username},
            )


@csrf_exempt
def accept_task(request):
    if request.method == "POST":
        task_id = request.POST.get("task_id")
        try:
            task = Tasks.objects.get(taskid=task_id)
            task.status = "in progress"
            task.save()
            Notification.objects.create(
                user_email=request.session["mail"],
                message=f"The task has been accepted by {request.session['mail']}",
            )
            return JsonResponse({"message": "Task accepted and status updated."})
        except Tasks.DoesNotExist:
            return JsonResponse({"message": "Task not found."}, status=404)

    return JsonResponse({"message": "Invalid request method."}, status=405)


@csrf_exempt
def accept_website_task(request):
    if request.method == "POST":
        task_id = request.POST.get("task_id")
        try:
            task = WebsiteTasks.objects.get(task_id=task_id)
            task.status = "in progress"
            task.save()
            Notification.objects.create(
                user_email=request.session["mail"],
                message=f"The website task has been accepted by {request.session['mail']}",
            )
            return JsonResponse({"message": "Task accepted and status updated."})
        except WebsiteTasks.DoesNotExist:
            return JsonResponse({"message": "Task not found."}, status=404)

    return JsonResponse({"message": "Invalid request method."}, status=405)


# def requirements_met(requirements, pylint_output):
#     # For simplicity, let's assume requirements are simple keywords the tester needs to check in the pylint report
#     required_keywords = requirements.split('\n')  # Split the requirements by newline if there are multiple
#     print(pylint_output)
#     print(required_keywords)
#     for keyword in required_keywords:
#         print(keyword)
#         if keyword not in pylint_output:
#             return False
#     return True


def requirements_met(requirements, pylint_output):

    requirements_list = requirements.split("\n")
    pylint_output_list = pylint_output.split("\n")
    result = []

    for requirement in requirements_list:
        if "indentation" in requirement.lower():
            for i in pylint_output_list:
                if re.search(r"IndentationError", i) or re.search(r"indentation", i):
                    result.append(i)

        # Check for line length requirement
        if "line length" in requirement.lower():
            for i in pylint_output_list:
                if re.search(r"Line too long", i):
                    result.append(i)

        # Check for undefined variable requirement
        if "undefined variable" in requirement.lower():
            for i in pylint_output_list:
                if re.search(r"Undefined variable", i):
                    result.append(i)

        # Check for naming conventions
        if "naming convention" in requirement.lower():
            for i in pylint_output_list:
                if re.search(r"[A-Z]", i):
                    result.append(i)

        # Check for docstring requirement
        if "docstring" in requirement.lower():
            for i in pylint_output_list:
                if re.search(r"(function|method|class) a docstring", i):
                    result.append(i)

        if "whitespace" in requirement.lower():
            for i in pylint_output_list:
                if re.search(r"whitespace", i):
                    result.append(i)

    # If no requirement was satisfied, return False
    print(result)
    return result


@csrf_exempt
def test_script(request):
    task = request.POST.get("task_id")
    obj = Tasks.objects.get(taskid=int(task))

    script_id = obj.script_id
    data = {}
    if request.method == "POST":
        script_obj = Scripts.objects.get(scriptid=int(script_id))
        script_path = script_obj.upfile.path
        requirements = script_obj.requirements
        print("Test File->", script_path)

        try:
            result = subprocess.run(
                ["pylint", script_path], capture_output=True, text=True
            )
            pylint_output = result.stdout
            test_result = requirements_met(requirements, pylint_output)
            if len(test_result) > 0:  # You'll need to implement this logic
                print("Success")
                obj.status = "test done"
                obj.save()
                Notification.objects.create(
                    user_email=request.session["mail"],
                    message=f"The testing of {script_obj.filename} has been completed successfully.",
                )
            else:
                print("Failed")
                obj.status = "test failed"
                obj.save()
                Notification.objects.create(
                    user_email=request.session["mail"],
                    message=f"The testing of {script_obj.filename} has failed.",
                )

            if len(test_result) > 0:
                request.session["report"] = "\n".join(test_result)

            else:
                request.session["report"] = pylint_output
            request.session["filename"] = script_obj.filename
            # task = Tasks.objects.get(taskid=int(task))
            # task.status = 'test done'
            # task.save()
            # Notification.objects.create(user_email=request.session['mail'],message=f"The testing of {script_obj.filename} has been completed by {request.session['mail']}.")
            return JsonResponse(data, safe=False)
            return render(
                request,
                "report.html",
                {"report": pylint_output, "filename": script_obj.filename},
            )

        except Exception as e:
            return HttpResponse(f"Error running pylint: {e}", status=500)

    return HttpResponse("Invalid request method", status=405)


@csrf_exempt
def review_website(request):
    task_id = request.POST.get("task_id")
    task = WebsiteTasks.objects.get(task_id=task_id)
    request.session["task_id"] = task_id
    return JsonResponse({"message": "Reviewing website"})  # Placeholder

def review_website_page(request):
    if "task_id" in request.session:
        task_id = request.session["task_id"]
        task = WebsiteTasks.objects.get(task_id=task_id)
        return render(request, "review_website_page.html", {"task": task})
    else:
        return render(request, "review_website_page.html")

def report_page(request):
    if "report" in request.session:
        report = request.session["report"]
        filename = request.session["filename"]
        del request.session["report"]
        del request.session["filename"]
        return render(request, "report.html", {"report": report, "filename": filename})
    else:
        return render(request, "report.html")


def tester_review_script(request):
    tasks = Tasks.objects.filter(
        Q(status="test done") | Q(status="test failed")
    ).select_related("script")

    task_data = []
    for task in tasks:
        script = task.script
        task_data.append(
            {
                "task": task,
                "requirements": script.requirements,
            }
        )

    return render(request, "tester_review_script.html", {"tasks": tasks})


@csrf_exempt
def submit_report(request):
    if request.method == "POST":
        task_id = request.POST.get("task_id")
        priority = request.POST.get("priority")
        description = request.POST.get("description")
        review_date = request.POST.get("review_date")
        mail = request.session["mail"]
        usr_obj = User.objects.get(email=mail)
        created_by = usr_obj.username

        try:
            task = Tasks.objects.get(taskid=task_id)
            Report.objects.create(
                priority_level=priority,
                description=description,
                taskid=task,
                created_by=created_by,
                created_date=review_date,
            )
            return JsonResponse({"message": "Review submitted successfully"})
        except Tasks.DoesNotExist:
            return JsonResponse({"error": "Task not found"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def submit_website_report(request):
    if request.method == "POST":
        task_id = request.POST.get("task_id")
        priority = request.POST.get("priority")
        description = request.POST.get("description")
        review_date = request.POST.get("review_date")
        print(f"Task ID: {task_id}, Priority: {priority}, Description: {description}, Review Date: {review_date}")
        mail = request.session["mail"]
        usr_obj = User.objects.get(email=mail)
        created_by = usr_obj.username

        try:
            task = WebsiteTasks.objects.get(task_id=task_id)
            task.status = "test done"
            task.save()
            WebsiteReport.objects.create(
                priority_level=priority,
                description=description,
                task_id=task,
                created_by=created_by,
                created_date=review_date,
            )
            print("Review submitted successfully")
            return JsonResponse({"message": "Review submitted successfully"})
        except WebsiteTasks.DoesNotExist:
            return JsonResponse({"error": "Task not found"}, status=400)
        except Exception as e:
            print(f"Error submitting review: {e}")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
@never_cache
def summarize(request):
    reportid = request.POST.get("id")
    rep_obj = Report.objects.get(repid=int(reportid))
    desc = rep_obj.description
    level = rep_obj.priority_level
    filename = rep_obj.taskid.script.filename
    text = "The priority of " + level + " level."
    text = text + " " + desc
    print(text)
    try:
        summarizer = pipeline("summarization")
        summary = summarizer(text, max_length=50, min_length=30, do_sample=False)
        print("sum:", summary)
        print(summary[0]["summary_text"])
        data = {}
        data["filename"] = filename
        data["summary"] = summary[0]["summary_text"]
    except Exception as e:
        print(f"Error in summarization pipeline: {e}")
        data = {"error": "Summarization failed"}

    return JsonResponse(data, safe=False)


@csrf_exempt
@never_cache
def dev_summarize(request):
    print("dev_summarize()")
    reportid = request.POST.get("id")
    rep_obj = Report.objects.get(repid=int(reportid))
    desc = rep_obj.description
    level = rep_obj.priority_level
    filename = rep_obj.taskid.script.filename
    text = "The priority of " + level + " level."
    text = text + " " + desc
    print(text)
    summarizer = pipeline("summarization")
    summary = summarizer(text, max_length=150, min_length=30, do_sample=False)
    print("sum:", summary)
    print(summary[0]["summary_text"])
    data = {}
    data["filename"] = filename
    data["summary"] = summary[0]["summary_text"]

    return JsonResponse(data, safe=False)


def completed_reports(request):
    if "mail" in request.session:
        mail = request.session["mail"]
        usr_obj = User.objects.get(email=mail)
        userid = usr_obj.username
        print("id->", userid)
        task_obj = Tasks.objects.filter(assign_to=userid)
        website_task_obj = WebsiteTasks.objects.filter(assign_to=userid)
        reports = Report.objects.filter(taskid__in=task_obj)
        websiteReports = WebsiteReport.objects.filter(task_id__in=website_task_obj)
        print("reports->", reports)
        return render(request, "completed_reports.html", {"reports": reports, "websiteReports": websiteReports})


def notifications(request):
    email = request.session["mail"]
    if not email:
        return JsonResponse({"error": "User not logged in"}, status=403)

    notifications = Notification.objects.filter(is_read=False).order_by("-created_at")

    # Mark notifications as read after viewing

    return render(request, "notification.html", {"notifications": notifications})


def mark_as_read(request):

    Notification.objects.filter(is_read=False).update(is_read=True)
    return HttpResponse("<script>window.location.href='/admin_home/';</script>")
