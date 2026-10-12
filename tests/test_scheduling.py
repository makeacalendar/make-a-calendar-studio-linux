import unittest
from datetime import date, timedelta

from make_a_calendar_studio.holidays import federal_holidays
from make_a_calendar_studio.scheduling import (add_business_days, business_days, payroll_dates,
                                                fiscal_months, retail_periods, retail_year_start, retail_year_weeks,
                                                shift_days)


class SchedulingTests(unittest.TestCase):
    def test_observed_federal_dates_include_cross_year_new_year(self):
        self.assertEqual(federal_holidays(2021)[date(2021,7,5)],"Independence Day")
        self.assertEqual(federal_holidays(2021)[date(2021,12,24)],"Christmas Day")
        self.assertEqual(federal_holidays(2021)[date(2021,12,31)],"New Year's Day")
        self.assertEqual(federal_holidays(2023)[date(2023,1,2)],"New Year's Day")

    def test_business_days_inclusive_holiday_exclusion_and_reverse_add(self):
        self.assertEqual(business_days(date(2026,10,9),date(2026,10,12)),2)
        self.assertEqual(business_days(date(2026,10,9),date(2026,10,12),holidays={date(2026,10,12)}),1)
        self.assertEqual(business_days(date(2026,10,9),date(2026,10,12),inclusive=False),1)
        self.assertEqual(add_business_days(date(2026,10,9),1),date(2026,10,12))
        self.assertEqual(add_business_days(date(2026,10,12),-1),date(2026,10,9))
        # Sunday and Monday are weekends for this location; the remaining days count as workdays.
        self.assertEqual(business_days(date(2026,10,11),date(2026,10,13),weekend=(6,0)),1)
        with self.assertRaises(ValueError): add_business_days(date(2026,10,12),1,weekend=tuple(range(7)))

    def test_retail_patterns_and_53_week_extension(self):
        for year in range(2000,2040):
            for pattern in ("4-4-5","4-5-4","5-4-4"):
                periods=retail_periods(year,pattern)
                self.assertEqual(len(periods),12)
                self.assertEqual(periods[0][1],retail_year_start(year))
                self.assertEqual(periods[-1][2]+timedelta(days=1),retail_year_start(year+1))
                weeks=retail_year_weeks(year)
                self.assertIn(weeks,(52,53))
                self.assertEqual(sum((end-start).days+1 for _,start,end in periods),weeks*7)

    def test_civil_fiscal_months_roll_across_year(self):
        months=fiscal_months(2026,10)
        self.assertEqual(len(months),12)
        self.assertEqual(months[0][1],date(2026,10,1))
        self.assertEqual(months[-1][1],date(2027,9,1))
        self.assertEqual(months[-1][2],date(2027,9,30))

    def test_payroll_frequencies_and_short_month_clamping(self):
        biweekly=payroll_dates(date(2026,1,1),date(2026,1,31),"biweekly",anchor=date(2026,1,1))
        self.assertEqual(biweekly,(date(2026,1,1),date(2026,1,15),date(2026,1,29)))
        monthly=payroll_dates(date(2026,2,1),date(2026,2,28),"monthly",day=31)
        self.assertEqual(monthly,(date(2026,2,28),))
        semi=payroll_dates(date(2026,2,1),date(2026,2,28),"semimonthly")
        self.assertEqual(semi,(date(2026,2,15),date(2026,2,28)))

    def test_shift_phase_is_preserved(self):
        days=shift_days(date(2026,1,1),date(2026,1,14),anchor=date(2026,1,1),pattern="2-2-3")
        self.assertEqual(len(days),14)
        self.assertEqual(sum(working for _,working in days),7)
        self.assertEqual(days[7][1],False)
        self.assertEqual(days[9][1],True)


if __name__=="__main__": unittest.main()
