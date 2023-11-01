from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import io
import base64
import datetime
import json
import calendar

@login_required(login_url='/accounts/login')
def index(request):
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)  # Use get_page directly


    context = {
        'expenses': expenses,
        'page_obj': page_obj,
    }
    return render(request, 'expenses/index.html', context)

@login_required(login_url='/accounts/login')
def add_expense(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'expenses/add_expense.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/add_expense.html', context)
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/add_expense.html', context)

        Expense.objects.create(owner=request.user, amount=amount, date=date,
                               category=category, description=description)
        messages.success(request, 'Expense saved successfully')

        return redirect('expenses')

def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/accounts/login')
def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories
    }
    if request.method == 'GET':
        return render(request, 'expenses/edit_expense.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit_expense.html', context)
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/edit_expense.html', context)

        expense.owner = request.user
        expense.amount = amount
        expense. date = date
        expense.category = category
        expense.description = description

        expense.save()
        messages.success(request, 'Expense updated  successfully')

        return redirect('expenses')

@login_required(login_url='/accounts/login')
def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense removed')
    return redirect('expenses')

@login_required(login_url='/accounts/login')
def expense_category_summary(request, period):
    todays_date = datetime.date.today()
    if period == 'day':
        start_date = todays_date
        end_date = todays_date
    elif period == 'month':
        start_date = todays_date.replace(day=1)
        end_date = todays_date
    elif period == 'year':
        start_date = todays_date.replace(month=1, day=1)
        end_date = todays_date.replace(month=12, day=31)
    else:
        # Handle an invalid period gracefully, you can redirect or show an error message.
        return HttpResponseBadRequest("Invalid period")

    expenses = Expense.objects.filter(
        owner=request.user,
        date__gte=start_date,
        date__lte=end_date
    )

    finalrep = {}
    total_expenses = 0

    def get_category(expense):
        return expense.category

    category_list = list(set(map(get_category, expenses)))

    for category in category_list:
        filtered_by_category = expenses.filter(category=category)
        total_amount = sum(item.amount for item in filtered_by_category)
        finalrep[category] = total_amount
        total_expenses += total_amount

    context = {
        'expense_category_data': finalrep,
        'total_expenses': total_expenses,
        'period': period,
    }

    return render(request, 'expenses/expense_category_summary.html', context)

