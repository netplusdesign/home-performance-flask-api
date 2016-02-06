import chartingperformance
import unittest
import json

class ChartingPerformanceTestCase(unittest.TestCase):

    def setUp(self):
        #self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        chartingperformance.app.config['TESTING'] = True
        self.app = chartingperformance.app.test_client()
        #flaskr.init_db()

    def tearDown(self):
        pass
        #os.close(self.db_fd)
        #os.unlink(flaskr.app.config['DATABASE'])

    def test_error_page(self):
        rv = self.app.get('/api/house/')
        json_rv = json.loads(rv.data)
        assert json_rv['error'] == 'Not found'

    def test_houses(self):
        rv = self.app.get('/api/houses/')
        json_rv = json.loads(rv.data)
        assert json_rv['houses'][0]['house_id'] == 0

    def test_devices(self):
        rv = self.app.get('/api/houses/0/devices/')
        json_rv = json.loads(rv.data)
        assert len(json_rv['devices']) == 11

    def test_circuits(self):
        rv = self.app.get('/api/houses/0/circuits/')
        json_rv = json.loads(rv.data)
        assert len(json_rv['circuits']) == 23
        assert json_rv['circuits'][0]['circuit_id'] == 'adjusted_load'
        assert json_rv['circuits'][0]['name'] == 'Net'

    def test_defaults_months(self):
        rv = self.app.get('/api/houses/0/views/default/') # ensure default value is working
        json_rv = json.loads(rv.data)
        assert json_rv['house']['id'] == 0

    def test_defaults_days(self):
        rv = self.app.get('/api/houses/0/views/default/?interval=days')
        json_rv = json.loads(rv.data)
        assert json_rv['limits']['start_date'] == '2012-02-01 00:00:00'

    def test_defaults_years(self):
        rv = self.app.get('/api/houses/0/views/default/?interval=years')
        assert 'Interval \'years\' does not exist' in rv.data

    def x_test_views_summary_days(self): # errors not propagating, long term fix
        rv = self.app.get('/api/houses/0/views/summary/?interval=days&start=2012-01-01&duration=1year')
        json_rv = json.loads(rv.data)
        assert 'Interval \'days\' does not exist' in rv.data

    def test_views_summary_days(self):
        rv = self.app.get('/api/houses/0/views/summary/?interval=days&start=2014-01-01&duration=31days')
        json_rv = json.loads(rv.data)
        assert len(json_rv['days']) == 31
        assert json_rv['days'][0]['net'] == 22.0340000000
        assert json_rv['totals']['net'] == 630.9560000000

    def test_views_summary_months(self):
        rv = self.app.get('/api/houses/0/views/summary/?interval=months&start=2012-01-01&duration=1year')
        json_rv = json.loads(rv.data)
        assert len(json_rv['months']) == 12
        assert json_rv['totals']['net'] == -3255.785

    def test_views_summary_years(self):
        rv = self.app.get('/api/houses/0/views/summary/?interval=years&start=2012-01-01&duration=1year')
        json_rv = json.loads(rv.data)
        assert len(json_rv['years']) == 1
        assert json_rv['totals']['net'] == -3255.785

    def test_views_summary_years_no_start_or_end(self):
        rv = self.app.get('/api/houses/0/views/summary/?interval=years')
        json_rv = json.loads(rv.data)
        assert len(json_rv['years']) == 3
        assert json_rv['totals']['net'] == -4864.293712758

    def test_views_summary_months_no_duration(self):
        rv = self.app.get('/api/houses/0/views/summary/?interval=months&start=2013-12-01')
        json_rv = json.loads(rv.data)
        assert len(json_rv['months']) == 13
        assert json_rv['totals']['net'] == 412.487287242

    def test_views_summary_months_no_start(self):
        rv = self.app.get('/api/houses/0/views/summary/?interval=months&end=2013-01-01')
        json_rv = json.loads(rv.data)
        assert len(json_rv['months']) == 12
        assert json_rv['totals']['net'] == -3255.785


    def test_views_generation_months(self):
        rv = self.app.get('/api/houses/0/views/generation/?interval=months&start=2013-01-01&duration=4months')
        json_rv = json.loads(rv.data)
        assert len(json_rv['months']) == 4
        assert json_rv['totals']['actual'] == -2465.356

    def test_views_generation_days(self):
        rv = self.app.get('/api/houses/0/views/generation/?interval=days&start=2013-01-01&duration=1month')
        json_rv = json.loads(rv.data)
        assert len(json_rv['days']) == 31
        assert json_rv['totals']['actual'] == -478.374

    def test_views_generation_hours(self):
        rv = self.app.get('/api/houses/0/views/generation/?interval=hours&start=2014-01-01&duration=3days')
        json_rv = json.loads(rv.data)
        assert len(json_rv['hours']) == 72
        assert json_rv['totals']['actual'] == -14.660


    def test_views_hdd_months(self):
        rv = self.app.get('/api/houses/0/views/hdd/?interval=months&start=2013-01-01&duration=4months')
        json_rv = json.loads(rv.data)
        assert len(json_rv['months']) == 4
        assert json_rv['totals']['actual'] == 3809.332
        assert json_rv['coldest_hour']['temperature'] == -7.089
        assert json_rv['coldest_day']['temperature'] == 60.770

    def test_views_temperature_years(self):
        rv = self.app.get('/api/houses/0/views/temperature/?interval=years&location=0')
        json_rv = json.loads(rv.data)
        assert len(json_rv['years']) == 4
        assert json_rv['totals']['avg_temperature'] == 49.5175434
        assert json_rv['totals']['max_temperature'] == 95.135
        assert json_rv['years'][0]['sum_hdd'] == 4759.847
        assert json_rv['years'][0]['avg_temperature'] == 53.5261340

    def test_views_water_months(self):
        rv = self.app.get('/api/houses/0/views/water/?interval=months&start=2013-01-01&duration=12months')
        json_rv = json.loads(rv.data)
        assert len(json_rv['months']) == 12
        assert json_rv['totals']['cold'] == 16253.4
        assert json_rv['totals']['hot'] == 7868.9
        assert json_rv['totals']['main'] == 24122.3
        assert json_rv['totals']['water_heater'] == 2078.042
        assert json_rv['totals']['water_pump'] == 63.780


    def test_views_usage_months_summary(self):
        rv = self.app.get('/api/houses/0/views/usage/?interval=months&start=2013-01-01&duration=12months')
        json_rv = json.loads(rv.data)
        assert json_rv['view'] == 'usage.summary'
        #assert json_rv['totals']['actual'] == 7206.154
        assert len(json_rv['circuits']) == 20
        for circuit in json_rv['circuits']:
            if circuit['circuit_id'] == 'used':
                assert circuit['actual'] == 7206.154
                assert circuit['name'] == 'Used'
            if circuit['circuit_id'] == 'water_heater':
                assert circuit['actual'] == 2078.042
                assert circuit['name'] == 'Water heater'
            if circuit['circuit_id'] == 'all_other':
                assert circuit['actual'] == 3098.636

    def test_views_usage_months_summary_2014(self):
        rv = self.app.get('/api/houses/0/views/usage/?interval=months&start=2014-01-01&duration=12months')
        json_rv = json.loads(rv.data)
        assert json_rv['view'] == 'usage.summary'
        for circuit in json_rv['circuits']:
            if circuit['circuit_id'] == 'all_other':
                assert circuit['actual'] == 1248.621306547

    def test_views_usage_months_all(self):
        rv = self.app.get('/api/houses/0/views/usage/?interval=months&start=2013-01-01&duration=12months&circuit=all')
        json_rv = json.loads(rv.data)
        assert json_rv['view'] == 'usage.all'
        assert len(json_rv['months']) == 12
        assert json_rv['totals']['actual'] == 7206.154
        assert json_rv['totals']['budget'] == 5950
        assert json_rv['months'][0]['date'] == '2013-01-01'
        assert json_rv['months'][0]['actual'] == 880.949
        assert json_rv['months'][0]['budget'] == 800
        assert json_rv['circuit']['circuit_id'] == 'all'
        assert json_rv['circuit']['name'] == 'All monitored circuits'
        assert json_rv['circuit']['description'] == 'Everything that is monitored (alias)'

    def test_views_usage_days_all(self):
        rv = self.app.get('/api/houses/0/views/usage/?interval=days&start=2013-01-01&duration=1month&circuit=all')
        json_rv = json.loads(rv.data)
        assert json_rv['view'] == 'usage.all'
        assert len(json_rv['days']) == 31
        assert json_rv['totals']['actual'] == 880.949
        assert json_rv['months'][0]['date'] == '2013-01-01'

    def test_views_usage_hours_all(self):
        rv = self.app.get('/api/houses/0/views/usage/?interval=hours&start=2013-05-01&duration=3days&circuit=all')
        json_rv = json.loads(rv.data)
        assert json_rv['view'] == 'usage.all'
        assert len(json_rv['days']) == 31
        assert json_rv['totals']['actual'] == 880.949
        assert json_rv['months'][0]['date'] == '2013-01-01'

    def test_views_usage_months_ashp(self):
        rv = self.app.get('/api/houses/0/views/usage/?interval=months&start=2013-01-01&duration=12months&circuit=ashp&base=50')
        json_rv = json.loads(rv.data)
        assert json_rv['view'] == 'usage.ashp'
        assert len(json_rv['months']) == 12
        assert json_rv['totals']['actual'] == 1195.782
        assert round(json_rv['totals']['hdd'], 4) == 3366.5438
        assert json_rv['months'][0]['date'] == '2013-01-01'
        assert json_rv['months'][0]['actual'] == 282.305
        assert round(json_rv['months'][0]['hdd'],5) == 730.24137
        assert json_rv['circuit']['circuit_id'] == 'ashp'
        assert json_rv['circuit']['name'] == 'ASHP'
        assert json_rv['circuit']['description'] == 'Air-source heat pump'

    def test_views_usage_months_all_other(self):
        rv = self.app.get('/api/houses/0/views/usage/?interval=months&start=2013-01-01&duration=12months&circuit=all_other')
        json_rv = json.loads(rv.data)
        assert json_rv['view'] == 'usage.all_other'
        assert len(json_rv['months']) == 12
        assert json_rv['totals']['actual'] == 3098.636
        assert json_rv['months'][0]['date'] == '2013-01-01'
        assert json_rv['months'][0]['actual'] == 240.958
        assert json_rv['circuit']['circuit_id'] == 'all_other'
        assert json_rv['circuit']['name'] == 'All other'
        assert json_rv['circuit']['description'] == 'Everything that is not monitored (alias)'

    def test_views_usage_months_all_other_with_new_circuits_2014(self):
        rv = self.app.get('/api/houses/0/views/usage/?interval=months&start=2014-01-01&duration=12months&circuit=all_other')
        json_rv = json.loads(rv.data)
        assert len(json_rv['months']) == 12
        assert json_rv['totals']['actual'] == 1248.621306547
        assert json_rv['months'][4]['date'] == '2014-05-01'
        assert json_rv['months'][4]['actual'] == 49.741706954

    def test_views_usage_months_water_heater(self):
        rv = self.app.get('/api/houses/0/views/usage/?interval=months&start=2013-01-01&duration=12months&circuit=water_heater')
        json_rv = json.loads(rv.data)
        assert json_rv['view'] == 'usage.water_heater'
        assert len(json_rv['months']) == 12
        assert json_rv['totals']['actual'] == 2078.042
        assert json_rv['months'][0]['date'] == '2013-01-01'
        assert json_rv['months'][0]['actual'] == 255.815
        assert json_rv['circuit']['circuit_id'] == 'water_heater'
        assert json_rv['circuit']['name'] == 'Water heater'
        assert json_rv['circuit']['description'] == ''

    def test_views_usage_months_water_pump(self):
        rv = self.app.get('/api/houses/0/views/usage/?interval=months&start=2013-01-01&duration=12months&circuit=water_pump')
        json_rv = json.loads(rv.data)
        assert len(json_rv['months']) == 12
        assert json_rv['totals']['actual'] == 63.780
        assert json_rv['months'][0]['date'] == '2013-01-01'
        assert json_rv['months'][0]['actual'] == 5.916
        assert json_rv['circuit']['circuit_id'] == 'water_pump'
        assert json_rv['circuit']['name'] == 'Water pump'
        assert json_rv['circuit']['description'] == ''

    def test_views_usage_months_dryer(self):
        rv = self.app.get('/api/houses/0/views/usage/?interval=months&start=2013-01-01&duration=12months&circuit=dryer')
        json_rv = json.loads(rv.data)
        assert len(json_rv['months']) == 12
        assert json_rv['totals']['actual'] == 224.337
        assert json_rv['months'][0]['date'] == '2013-01-01'
        assert json_rv['months'][0]['actual'] == 33.748
        assert json_rv['circuit']['circuit_id'] == 'dryer'
        assert json_rv['circuit']['name'] == 'Dryer'
        assert json_rv['circuit']['description'] == 'Ventless'

    def test_views_usage_months_washer(self):
        rv = self.app.get('/api/houses/0/views/usage/?interval=months&start=2013-01-01&duration=12months&circuit=washer')
        json_rv = json.loads(rv.data)
        assert len(json_rv['months']) == 12
        assert json_rv['totals']['actual'] == 44.702
        assert json_rv['months'][0]['date'] == '2013-01-01'
        assert json_rv['months'][0]['actual'] == 5.006
        assert json_rv['circuit']['circuit_id'] == 'washer'
        assert json_rv['circuit']['name'] == 'Washer'
        assert json_rv['circuit']['description'] == 'Front loader'

    def test_views_basetemp_months(self):
        rv = self.app.get('/api/houses/0/views/basetemp/?interval=months&start=2013-01-01&duration=12months&base=65')
        json_rv = json.loads(rv.data)
        assert json_rv['interval'] == 'month'
        assert len(json_rv['points']) == 9
        assert json_rv['points'][0]['date'] == '2013-01-01 15:00:00'
        assert round(json_rv['points'][0]['hdd'], 6) == 639.533917
        assert json_rv['points'][0]['ashp'] == 237.8200
        assert json_rv['points'][0]['temperature'] == 23.5167189   # should be hdd
        assert json_rv['points'][0]['solar'] == -10.3790

    def test_views_basetemp_default(self):
        rv = self.app.get('/api/houses/0/views/basetemp/?interval=months&start=2013-01-01&duration=12months')
        json_rv = json.loads(rv.data)
        assert json_rv['base'] == '65'
        assert json_rv['interval'] == 'month'
        assert len(json_rv['points']) == 9
        assert json_rv['points'][0]['date'] == '2013-01-01 15:00:00'
        assert round(json_rv['points'][0]['hdd'], 6) == 639.533917
        assert json_rv['points'][0]['ashp'] == 237.8200
        assert json_rv['points'][0]['temperature'] == 23.5167189   # should be hdd
        assert json_rv['points'][0]['solar'] == -10.3790

    def test_views_chart(self):
        rv = self.app.get('/api/houses/0/views/chart/?interval=hours&start=2013-01-01&duration=1day')
        json_rv = json.loads(rv.data)
        assert json_rv['view'] == 'chart'
        assert len(json_rv['hours']) == 24
        assert json_rv['hours'][0]['date'] == '2013-01-01 00:00:00'
        assert json_rv['hours'][0]['net'] == 224
        assert json_rv['hours'][0]['solar'] == 0
        assert json_rv['hours'][0]['first_floor_temp'] == 65.851
        assert json_rv['hours'][0]['hdd'] == 1.417

    def test_views_heatmap(self):
        rv = self.app.get('/api/houses/0/views/heatmap/?interval=hours&start=2013-01-01&duration=1month')
        json_rv = json.loads(rv.data)
        assert json_rv['view'] == 'heatmap'
        assert len(json_rv['days']) == 31
        assert json_rv['days'][0]['date'] == '2013-01-01'
        assert json_rv['days'][0]['net'] == 26.881
        assert json_rv['days'][0]['solar'] == 0
        assert json_rv['days'][0]['outdoor_deg_min'] == 10.179
        assert json_rv['days'][0]['hdd'] == 40.752

if __name__ == '__main__':
    unittest.main()
