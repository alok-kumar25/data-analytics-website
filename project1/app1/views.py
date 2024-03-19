from django.shortcuts import render,redirect
from django.contrib.auth import authenticate , login , logout 
from django.contrib import messages
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt 
from .forms import SignUpForm
from django.http import HttpResponse
from django.http import JsonResponse
import pandas as pd
import os
import uuid
import base64
from io import BytesIO
from .models import Image
from django.core.files.base import ContentFile
from .models import Image
# Create your views here.
def home(request):
    if request.method == 'POST':
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(request , username = username , password = password )
        if user is not None:
            login(request,user)
            messages.success(request,"welcome !!")
            return redirect('home')
        else:
            messages.success(request,"Something went wrong please try again!!")
            return redirect('home')
    else:
        return render(request,'home.html',{})

def logout_user(request):
    logout(request)
    messages.success(request,"you have been logged out!!")
    return redirect('home')
 
def register_user(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			user = authenticate(username=username, password=password)
			login(request, user)
			messages.success(request, "You Have Successfully Registered! Welcome!")
			return redirect('home')
	else:
		form = SignUpForm()
		return render(request, 'register.html', {'form':form})

	return render(request, 'register.html', {'form':form})

TEMP_DIR = 'C:/python'

def upload_csv(request):
    if request.user.is_authenticated:
        if request.method == 'POST' and request.FILES.get('csv_file'):
            csv_file = request.FILES['csv_file']
            file_name = f'{uuid.uuid4()}.csv'
            file_path = os.path.join(TEMP_DIR, file_name)
            with open(file_path, 'wb') as f:
                for chunk in csv_file.chunks():
                    f.write(chunk)
            return redirect('report_with_file', file_name=file_name,t=1)
        else:
            messages.success(request,"please upload the file !!")
            return render(request,'home.html')
    else:
        messages.success(request,"You do not have access to this page please login ")
        return redirect('home')

def generate_plot(df,selected_columns,c):
    #charts for univariate
    if c =="box":
        plt.figure(figsize=(10, 6))
        sns.boxplot(y=df[selected_columns[0]])
        plt.title('Box Plot of '+str(selected_columns[0]))
        plt.ylabel(selected_columns[0])
        
    elif c =="pie":
        plt.figure(figsize=(10, 6))
        count = df[selected_columns[0]].value_counts()
        plt.pie(count, labels=count.index, autopct='%1.1f%%')
        plt.title('Pie Chart of '+str(selected_columns[0]))
        
    elif c == 'histogram':
        #plt.figure(figsize=(10, 6))
        sns.histplot(df[selected_columns[0]], bins=20, kde=True)
        plt.xlabel(selected_columns[0])
        plt.ylabel('Frequency')
        plt.title('Histogram of '+str(selected_columns[0]))
        
    elif c == 'bar':
        plt.figure(figsize=(10, 6))
        sns.barplot(x=df[selected_columns[0]],y=df[selected_columns[1]])
        plt.xlabel(selected_columns[0])
        plt.ylabel(selected_columns[1])
        plt.title('Bar Plot of '+str(selected_columns[0]))
        
    elif c == 'density':
        plt.figure(figsize=(10, 6))
        sns.kdeplot(df[selected_columns[0]], shade=True)
        plt.xlabel(selected_columns[0])
        plt.ylabel('Density')
        plt.title('density plot of '+str(selected_columns[0]))
        
    #plots for bi variate 
    
    elif c == "scatter":
        plt.figure(figsize=(10, 6))
        sns.regplot(x=df[selected_columns[0]],y=df[selected_columns[1]])
        plt.xlabel(selected_columns[0])
        plt.ylabel(selected_columns[1])
        plt.title('Scatter Plot')
        
    elif c == 'heatmap':
        df_isnum = df.select_dtypes(include='number')
        column_corr = df_isnum.corr()[selected_columns[0]]
        plt.figure(figsize=(10,6))
        sns.heatmap(column_corr.to_frame(),annot=True,cbar=False)
        plt.title("correlation")
        
    elif c == "pair":
        column_to_compare = selected_columns[0]
        sns.pairplot(df, x_vars=[column_to_compare], y_vars=df.columns.drop(column_to_compare), height=2.5)
        plt.suptitle(f'Pair Plot of {column_to_compare.capitalize()} vs Others', y=1.02)
        
    elif c == "joint":
        sns.jointplot(x=selected_columns[0], y=selected_columns[1], data=df, kind='hex')
        plt.title('Joint Plot of '+selected_columns[0]+" vs "+selected_columns[1])
        plt.xlabel(selected_columns[0])
        plt.ylabel(selected_columns[1])
        
    elif c == "line":
        plt.figure(figsize=(10, 6))
        sns.lineplot(x=df[selected_columns[0]],y=df[selected_columns[1]])
        plt.xlabel(selected_columns[0])
        plt.ylabel(selected_columns[1])
        plt.title('Line plot')
        
    elif c == "violin":
        plt.figure(figsize=(10, 6))
        sns.violinplot(x=df[selected_columns[0]],y=df[selected_columns[1]])
        plt.xlabel(selected_columns[0])
        plt.ylabel(selected_columns[1])
        plt.title('violin Plot')
    
    
    
    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    return plot_data

def add_image_db(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.POST.get('plot_data')
        if image:
            image_data = ContentFile(base64.b64decode(image), name='plot.png')
        user = request.user
        image_instance = Image.objects.create(user=user, title=title, description=description, image=image_data)
        return HttpResponse()

def reports(request, **kwargs):
    if request.user.is_authenticated:
        file_path = os.path.join(TEMP_DIR, kwargs.get('file_name'))
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df_slice = df.head()
            if request.method == "POST" and  request.POST.get('column1'):
                selected_column1 = request.POST.get('column1')
                selected_column2 = request.POST.get('column2')
                chart=request.POST.get('chart')
                chart_img=generate_plot(df,[selected_column1,selected_column2],chart)
                return render(request, 'reports.html', {'df': df, 'df_slice': df_slice,'plot_data':chart_img})
            return render(request, 'reports.html', {'df': df, 'df_slice': df_slice})
        else:
            return HttpResponse("CSV file not found.")
    else:
        messages.success("You do not have access to this page. Please login.")
        return redirect('home')

def show_saved_charts(request):
    if request.user.is_authenticated:
        
        user_images = Image.objects.filter(user=request.user)
        serialized_images = []
        for image in user_images:
            with open(image.image.path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")
            serialized_images.append({
                'title': image.title,
                'description': image.description,
                'image_data': image_data,
            })
        return render(request, 'saved_charts.html', {'serialized_images': serialized_images})
    else:
        messages.success(request,"please login to see your saved charts ")
        return redirect('home')