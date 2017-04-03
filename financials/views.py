from django.shortcuts import render
from django.views.generic import View, TemplateView
from financials.models import *
from financials.utils import *
from django.http import JsonResponse
from datetime import datetime as d, timedelta

# Create your views here.


class ProfileValues(View):

    def get(self, request, *args, **kwargs):
        self.user = request.user
        self.profile = CustomerProfile.objects.get(
            user=self.user)
        data = self.get_values()
        return JsonResponse(data, safe=False)

    def get_values(self, *args, **kwargs):
        all_gains = CalculateGains(self.user)
        values = all_gains.get_total_values()
        temp = {}
        temp['investment_amount'] = values['invested_amount']
        temp['committed_amount'] = self.profile.commited_amount
        temp['dividend'] = values['dividend']
        temp['realised_gains'] = values['realised_gains']
        temp['unrealised_gains'] = values['unrealised_gains']
        temp['current_market_value'] = values['current_value']
        xirr_arr = self.get_xirr(values['current_value'],values['total_units'])
        temp['xirr'] = xirr_arr[0]
        temp['xirr_nifty'] = xirr_arr[1]
        # temp['xirr_nifty'] = self.calculate_xirr()
        #self.get_portfolio(all_gains)
        return temp

    def get_xirr(self, cmv,total_quantity):
        transactions = Transactions.objects.filter(
            user=self.user).values_list('date_created', 'transaction_type', 'amount','quantity')
        cashflows = []
        nifty_cashflows = []
        for row in transactions:
            if row[1] == 'buy':
                cashflows.append((row[0].date(), -float(row[2])))
                nifty_cashflows.append((row[0].date(), -float(row[3])*get_nifty_cmp(row[0].date())))
            else:
                cashflows.append((row[0].date(), float(row[2])))
                nifty_cashflows.append((row[0].date(), float(row[3])*get_nifty_cmp(row[0].date())))
        cashflows.append((d.now().date(), float(cmv)))
        nifty_cashflows.append((d.now().date(), float(total_quantity)*get_nifty_cmp(d.now().date())))
        return round(xirr(cashflows)*100.0,2),round(xirr(nifty_cashflows)*100.0,2)

class Portfolio(View):

    def get(self, request, *args, **kwargs):
        self.user = request.user
        all_gains = CalculateGains(self.user)
        data = self.get_portfolio(all_gains)
        return JsonResponse(data, safe=False)

    def get_portfolio(self ,data):
        values = data.gains
        values1 = data.get_total_values()
        #scrip_name = get_scripname()
        columns = ['scrip_name', 'quantity', 'current_value','portfolio','dividend',
                    'realised_gains', 'unrealised_gains']
        temp = []
        for key, value in values.iteritems():
            if key:
                scrip = CompanyMaster.objects.get(scrip_code = key)
                name = scrip.scrip_name
                p = self.get_portfolio_percentage(value['invested_amount'],values1['invested_amount'])
                var = [name,value['total_units'],value['current_value'],p,value['dividend'],value['realised_gains'],value['unrealised_gains']]
                temp.append(var)
        data = {'columns': columns, 'data': temp}
        return data
    def get_portfolio_percentage(self,x,y):
        return round((float(x)/float(y))*100,2)
        

class Performance(View):

    def get(self, request, *args, **kwargs):
        self.datenow = d.now()
        self.user = request.user
        self.user_id = CustomerProfile.objects.filter(full_name = self.user).values_list('user_id')
        #self.profile = CustomerProfile.objects.get(
         #   user=self.user)
        #self.user_id = request.GET.get('user_id', False)
        data = self.get_performance_data(self.user_id)
        return JsonResponse(data, safe=False)

    def get_performance_data(self,user):
        #try:
            self.inception_date = self.get_inception_date()
            self.dates, self.custom_dates = self.get_all_dates(
                self.datenow - timedelta(days=365), d.date(d.now()))
            self.history = Transactions.objects.filter(user_id=self.user_id,date_created__gte=self.datenow - timedelta(days=365)).values_list(
                'scrip_code', 'date_created', 'quantity', 'transaction_type').order_by('date_created')
            holding_data = self.get_holdings()
            return holding_data
        #except:
        #    message = "User not exist"
        #    return JsonResponse(message, safe=False)

    def get_inception_date(self, *args, **kwargs):
        date = CustomerProfile.objects.filter(user=self.user_id).values_list(
            'date_joined').order_by('date_joined')[0]
        return date[0]
    def get_holdings(self, *args, **kwargs):
        temp = []
        for i, date in enumerate(self.custom_dates[:-1]):
            value = self.get_holding_details(date)
            #if value == 0:
            #    value = temp[-1][1]
            temp.append(
                [(self.dates[i] - d(1970, 1, 1).date()).total_seconds() * 1000, value])
        return temp

    def get_holding_details(self, date, *args, **kwargs):
        temp_data = []
        temp_delta = {}
        val = 0
        for row in self.history:
            qty = 0
            if row[1].date() < date:
                if row[0] in temp_delta:
                    if row[3] == 'buy':
                        qty = qty + int(row[2])
                        temp_delta[row[0]] += self.get_nav(date, qty, row)
                    elif row[3] == 'sell':
                        qty = qty - int(row[2])
                        temp_delta[row[0]] += self.get_nav(date, qty, row)
                else:
                    temp_delta[row[0]] = self.get_nav(date, int(row[2]), row)
        for key, value in temp_delta.iteritems():
            val += value
        return val

    def get_nav(self, date, quantity, row):
        dat = d.combine(date, d.min.time())
        try:
            var = StockValues.objects.filter(scrip_code=row[0], date=dat).order_by(
                'date').values_list('close_value', 'date')[:1]
        except:
            var = StockValues.objects.filter(scrip_code=row[0], date__lte=dat).order_by(
                'date').values_list('close_value', 'date')[::-1]
        if var:
            return var[0][0] * quantity
        else:
            return 0
    
    def get_all_dates(self, date, to_date):
        date = d.date(date)
        temp = date
        dates_list = []
        dates_list.append(temp)
        while temp <= to_date:
            temp = self.add_months(temp, 1)
            dates_list.append(temp)
        return dates_list, self.adjust_dates(dates_list)

    def add_months(self, sourcedate, months=1):
        month = sourcedate.month - 1 + months
        year = int(sourcedate.year + month / 12)
        month = month % 12 + 1
        day = '01'
        new_date = d.strptime(str(day) + str(month) + str(year), "%d%m%Y")
        return d.date(new_date)

    def adjust_dates(self, dates_list):
        temp = []
        holidays = [5]
        for date in dates_list:
            if date.month in holidays:
                new_date = date - timedelta(days=1)
                temp.append(self.near_friday(new_date))
            else:
                temp.append(self.near_friday(date))
        return tuple(temp)

    def near_friday(self, date):
        if date.weekday() > 4:
            return date - timedelta(days=date.weekday() - 4)
        else:
            return date

class Orders(View):
    def get(self, request, *args, **kwargs):
        self.user = request.user
        data = self.get_history(self.user)
        return JsonResponse({'columns': [], 'data': data}, safe=False)

    def get_history(self, person):
        orders = Transactions.objects.filter(user = person)
        temp = []
        for x in orders:
            data = []
            data.append(x.date_created)
            scrip = CompanyMaster.objects.get(scrip_code = x.scrip_code)
            data.append(scrip.scrip_name)
            data.append(x.quantity)
            data.append(x.price)
            data.append(x.amount)
            data.append(x.transaction_type)
            temp.append(data)
        return temp

class UserProfile(View):
    def get(self, request, *args, **kwargs):
        self.user = request.user
        data = self.get_profile_data(self.user)
        obj = self.set_dafault(data)
        return JsonResponse(obj, safe = False)

    def get_profile_data(self, user):
        profile = CustomerProfile.objects.filter(full_name = user)
        temp = []
        temp.append(profile)
        return temp

    def set_dafault(self, data):
        if isinstance(data, set):
            return list(data)



        
        

        
