from financials.models import *
import datetime


class CalculateGains(object):
    """docstring for ClaculateGains"""

    def __init__(self, user):
        super(CalculateGains, self).__init__()
        self.user = user
        self.trxns = self.get_transactions()
        self.gains = self.get_gains()

    def get_transactions(self):
        return Transactions.objects.filter(user=self.user).order_by('date_created')

    def get_gains(self):
        # totalquantity = 0
        # totalprice = 0
        # for trxn in self.sell_trans:
        # 	while trxn.date_created > buy_trans.date_created
        # 		if trxn.quantity > buy_trans.quantity
        temp = {}
        gains = {}
        for row in self.trxns:
            if row.scrip_code in temp:
                pass
            else:
                temp[row.scrip_code] = {
                    "buy": [],
                    "sell": [],
                    "dividend": 0
                }
            if row.scrip_code in gains:
                pass
            else:
                gains[row.scrip_code] = {
                    "realised_gains": 0
                }
            if row.transaction_type == 'sell':
                qty = float(row.quantity)
                amt = float(row.amount)
                buy_price = 0
                for i, lin in enumerate(temp[row.scrip_code]['buy']):
                    if lin[0] >= qty:
                        buy_price = qty * lin[1]
                        temp[row.scrip_code]['buy'][i] = [lin[0] - qty, lin[1]]
                        break
                    else:
                        buy_price += lin[0] * lin[1]
                        temp[row.scrip_code]['buy'].pop(i)
                        qty = qty - lin[0]
                gain = amt - buy_price
                gains[row.scrip_code]['realised_gains'] = gain

            elif row.transaction_type == 'buy':
                temp[row.scrip_code]['buy'].append(
                    [float(row.quantity), float(row.price)])
            elif row.transaction_type == 'dividend':
                temp[row.scrip_code]['dividend'] = temp[
                    row.scrip_code]['dividend'] + float(row.amount)
        all_gains = {}
        for key, value in temp.iteritems():
            qty_total = 0
            amount_total = 0
            for x in value["buy"]:
                qty_total = qty_total + x[0]
                amount_total = amount_total + (x[0] * x[1])
            cmv = qty_total * self.get_cmp(key)
            all_gains[key] = {
                "total_units": qty_total,
                "invested_amount": amount_total,
                "current_value": cmv,
                "unrealised_gains": cmv - amount_total,
                "realised_gains": gains[key]['realised_gains'],
                "dividend": temp[key]['dividend']
            }
        return all_gains

    def get_cmp(self, scrip_code):
        now = datetime.datetime.now()
        scrip = StockValues.objects.filter(
            scrip_code=scrip_code).order_by('-date').values_list('close_value')
        if scrip:
            return float(scrip[0][0])
        else:
            return 34.67

    def get_total_values(self):
        temp = {
            "total_units": 0,
            "invested_amount": 0,
            "current_value": 0,
            "unrealised_gains": 0,
            "realised_gains": 0,
            "dividend": 0
        }
        for k, v in self.gains.iteritems():
            temp['total_units'] = temp['total_units'] + v['total_units']
            temp['invested_amount'] = temp[
                'invested_amount'] + v['invested_amount']
            temp['current_value'] = temp['current_value'] + v['current_value']
            temp['unrealised_gains'] = temp[
                'unrealised_gains'] + v['unrealised_gains']
            temp['realised_gains'] = temp[
                'realised_gains'] + v['realised_gains']
            temp['dividend'] = temp['dividend'] + v['dividend']

        return temp


def secant_method(tol, f, x0):
    """
    Solve for x where f(x)=0, given starting x0 and tolerance.

    Arguments
    ----------
    tol: tolerance as percentage of final result. If two subsequent x values are with tol percent, the function will return.
    f: a function of a single variable
    x0: a starting value of x to begin the solver

    Notes
    ------
    The secant method for finding the zero value of a function uses the following formula to find subsequent values of x.

    x(n+1) = x(n) - f(x(n))*(x(n)-x(n-1))/(f(x(n))-f(x(n-1)))

    Warning
    --------
    This implementation is simple and does not handle cases where there is no solution. Users requiring a more robust version should use scipy package optimize.newton.

    """

    x1 = x0 * 1.1
    while (abs(x1 - x0) / abs(x1) > tol):
        x0, x1 = x1, x1 - f(x1) * (x1 - x0) / (f(x1) - f(x0))
    return x1


def xnpv(rate, cashflows):
    """
    Calculate the net present value of a series of cashflows at irregular intervals.

    Arguments
    ---------
    * rate: the discount rate to be applied to the cash flows
    * cashflows: a list object in which each element is a tuple of the form (date, amount), where date is a python datetime.date object and amount is an integer or floating point number. Cash outflows (investments) are represented with negative amounts, and cash inflows (returns) are positive amounts.

    Returns
    -------
    * returns a single value which is the NPV of the given cash flows.

    Notes
    ---------------
    * The Net Present Value is the sum of each of cash flows discounted back to the date of the first cash flow. The discounted value of a given cash flow is A/(1+r)**(t-t0), where A is the amount, r is the discout rate, and (t-t0) is the time in years from the date of the first cash flow in the series (t0) to the date of the cash flow being added to the sum (t).
    * This function is equivalent to the Microsoft Excel function of the same name.

    """

    chron_order = sorted(cashflows, key=lambda x: x[0])
    t0 = chron_order[0][0]  # t0 is the date of the first cash flow

    return sum([cf / (1 + rate)**((t - t0).days / 365.0) for (t, cf) in chron_order])


def xirr(cashflows, guess=0.1):
    """
    Calculate the Internal Rate of Return of a series of cashflows at irregular intervals.

    Arguments
    ---------
    * cashflows: a list object in which each element is a tuple of the form (date, amount), where date is a python datetime.date object and amount is an integer or floating point number. Cash outflows (investments) are represented with negative amounts, and cash inflows (returns) are positive amounts.
    * guess (optional, default = 0.1): a guess at the solution to be used as a starting point for the numerical solution.

    Returns
    --------
    * Returns the IRR as a single value

    Notes
    ----------------
    * The Internal Rate of Return (IRR) is the discount rate at which the Net Present Value (NPV) of a series of cash flows is equal to zero. The NPV of the series of cash flows is determined using the xnpv function in this module. The discount rate at which NPV equals zero is found using the secant method of numerical solution.
    * This function is equivalent to the Microsoft Excel function of the same name.
    * For users that do not have the scipy module installed, there is an alternate version (commented out) that uses the secant_method function defined in the module rather than the scipy.optimize module's numerical solver. Both use the same method of calculation so there should be no difference in performance, but the secant_method function does not fail gracefully in cases where there is no solution, so the scipy.optimize.newton version is preferred.

    """

    return secant_method(0.0001, lambda r: xnpv(r, cashflows), guess)

def get_nifty_cmp(date):
	return 100.0
