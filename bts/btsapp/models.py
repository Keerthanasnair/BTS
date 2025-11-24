from django.db import models
import yaml
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

# Function to load conversations from a YAML file
def load_conversations_from_yaml(yaml_file):
    with open(yaml_file, 'r') as file:
        data = yaml.safe_load(file)
    return data['conversations']


def load_conversations_from_yaml(yaml_file):
    with open(yaml_file, 'r') as file:
        data = yaml.safe_load(file)
        if not isinstance(data, dict):
            raise ValueError("YAML file content must be a dictionary.")
        if 'conversations' not in data:
            raise KeyError("'conversations' key is missing in the YAML file.")
        if not isinstance(data['conversations'], list):
            raise ValueError("'conversations' must be a list of conversations.")
        return data['conversations']


# Function to clean the YAML file
def clean_yaml_file(file_path):
    with open(file_path, 'rb') as file:
        content = file.read()
    # Remove null bytes (if any)
    content = content.replace(b'\x00', b'')
    with open(file_path, 'wb') as file:
        file.write(content)

# Clean the YAML file before training
clean_yaml_file('btsapp/static/custom_conversation.yml')

# Create and configure the chatbot
chatbot = ChatBot(
    'BugTrackingBot',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    logic_adapters=[
        'chatterbot.logic.BestMatch',
        'chatterbot.logic.MathematicalEvaluation',
    ],
    database_uri='sqlite:///database.db'  # Configure the database
)

# Load conversations and train the chatbot
conversations = load_conversations_from_yaml('btsapp/static/custom_conversations.yml')
# for conv in conversations:
#     print(conv)
# all_conversations = [conv for conv_list in conversations.values() for conv in conv_list]
all_conversations = [conv for conv_list in conversations for conv in conv_list]


trainer = ListTrainer(chatbot)
trainer.train(all_conversations)




class User(models.Model):
    userid = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50)
    email=models.CharField(max_length=100)
    password=models.CharField(max_length=100)
    role = models.CharField(max_length=20)


class Scripts(models.Model):
    scriptid = models.AutoField(primary_key=True)
    filename = models.CharField(max_length=200)
    upfile = models.FileField(upload_to='uploaded_scripts/')
    devid = models.ForeignKey(User, on_delete=models.CASCADE)
    requirements = models.TextField()  
    created_date = models.CharField(max_length=100)
    status = models.CharField(max_length=30)
    assigned_to = models.CharField(max_length=50)


class Tasks(models.Model):
    taskid =models.AutoField(primary_key=True)
    script=models.ForeignKey(Scripts,on_delete=models.CASCADE)
    assign_to=models.CharField(max_length=50)
    script_from=models.CharField(max_length=50)
    status=models.CharField(max_length=30)
    received_date=models.CharField(max_length=100)
    requirements=models.TextField(default='no requirements provided')


class Report(models.Model):
    repid=models.AutoField(primary_key=True)
    priority_level=models.CharField(max_length=20)
    description=models.CharField(max_length=200)
    taskid=models.ForeignKey(Tasks, on_delete=models.CASCADE)
    created_by=models.CharField(max_length=50)
    created_date=models.CharField(max_length=50)


class Notification(models.Model):
    notif_id = models.AutoField(primary_key=True)
    user_email = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
