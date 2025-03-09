from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy

from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .forms import CustomRegistrationForm, CustomLoginForm, TaskForm
from django.contrib.auth import login

from .models import Task

def login_view(request):
    form = CustomLoginForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('tasks')
            else:
                form.add_error(None, 'Invalid username or password.')
    else:
        form = CustomLoginForm()
    return render(request, 'base/login.html', {'form': form})
    
def register_view(request):
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect('tasks')
    else:
        form = CustomRegistrationForm()
    return render(request, 'base/register.html', {'form': form})
    
@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    count = tasks.filter(complete=False).count()

    search_input = request.GET.get('search-area', '')
    if search_input:
        tasks = tasks.filter(title__startswith=search_input)


    context = {
        'tasks': tasks,
        'count': count,
        'search_input': search_input,
    }
    return render(request, 'base/task_list.html', context)

@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, id=pk, user=request.user)
    context = {'task': task}
    return render(request, 'base/task.html', context)

class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)
    

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('tasks')
    else:
        form = TaskForm()
    return render(request, 'base/task_form.html', {'form': form})


@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, id=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('tasks')
    else:
        form = TaskForm(instance=task)
    return render(request, 'base/task_form.html', {'form': form})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, id=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')
    return render(request, 'base/task_confirm_delete.html', {'task': task})