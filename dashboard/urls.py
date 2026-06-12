from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Core
    path('',                                    views.dashboard_home,       name='home'),
    path('search/',                             views.search_area,          name='search'),
    path('history/',                            views.search_history,       name='history'),
    path('saved/',                              views.saved_areas,          name='saved'),
    path('save/<int:area_id>/',                 views.save_area,            name='save_area'),
    path('unsave/<int:area_id>/',               views.unsave_area,          name='unsave_area'),
    path('area/<int:area_id>/',                 views.area_detail,          name='area_detail'),

    # Maps & Analysis
    path('heatmap/',                            views.heatmap_view,         name='heatmap'),
    path('heatmap/data/',                       views.heatmap_data,         name='heatmap_data'),
    path('compare/',                            views.compare_areas,        name='compare'),
    path('compare/data/',                       views.compare_data,         name='compare_data'),
    path('route/',                              views.route_checker,        name='route'),
    path('route/analyze/',                      views.route_analyze,        name='route_analyze'),

    # Reports & Data
    path('report/<int:area_id>/',               views.download_report,      name='download_report'),
    path('trends/<int:area_id>/',               views.crime_trends,         name='crime_trends'),
    path('review/<int:area_id>/',               views.submit_review,        name='submit_review'),
    path('forecast/<int:area_id>/',             views.risk_forecast,        name='forecast'),

    # Alerts & Notifications
    path('alerts/',                             views.manage_alerts,        name='alerts'),
    path('alerts/subscribe/<int:area_id>/',     views.subscribe_alert,      name='subscribe_alert'),
    path('alerts/unsubscribe/<int:pk>/',        views.unsubscribe_alert,    name='unsubscribe_alert'),
    path('whatsapp-alert/<int:area_id>/',       views.send_whatsapp_alert,  name='whatsapp_alert'),
    path('share/<int:area_id>/',                views.share_report,         name='share_report'),

    # Crime Feed & Reporting
    path('feed/',                               views.crime_feed,           name='crime_feed'),
    path('feed/data/',                          views.crime_feed_data,      name='crime_feed_data'),
    path('report-crime/',                       views.report_crime,         name='report_crime'),
    path('my-reports/',                         views.my_reports,           name='my_reports'),

    # NEW: Live Location Safety
    path('live-safety/',                        views.live_safety,          name='live_safety'),
    path('live-safety/check/',                  views.live_safety_check,    name='live_safety_check'),

    # NEW: Crime Time Analysis
    path('time-analysis/<int:area_id>/',        views.crime_time_analysis,  name='time_analysis'),
    path('time-analysis/data/<int:area_id>/',   views.time_analysis_data,   name='time_analysis_data'),

    # NEW: City Safety Leaderboard
    path('leaderboard/',                        views.safety_leaderboard,   name='leaderboard'),

    # NEW: SOS Emergency Button
    path('sos/',                                views.sos_page,             name='sos'),
    path('sos/send/',                           views.sos_send,             name='sos_send'),
    path('sos/resolve/<int:pk>/',               views.sos_resolve,          name='sos_resolve'),

    # NEW: Safety Journey Tracker
    path('journey/',                            views.journey_list,         name='journey'),
    path('journey/start/',                      views.journey_start,        name='journey_start'),
    path('journey/end/<int:pk>/',               views.journey_end,          name='journey_end'),
    path('journey/status/<int:pk>/',            views.journey_status,       name='journey_status'),

    # NEW: Anonymous Tip System
    path('anonymous-tip/',                      views.anonymous_tip,        name='anonymous_tip'),
    path('tips/',                               views.tips_list,            name='tips_list'),
    path('tips/upvote/<int:pk>/',               views.tip_upvote,           name='tip_upvote'),

    # NEW: Crime Calendar
    path('calendar/',                           views.crime_calendar,       name='calendar'),
    path('calendar/data/',                      views.calendar_data,        name='calendar_data'),

    # NEW: Nearby Safe Places
    path('nearby-safe/<int:area_id>/',          views.nearby_safe_places,   name='nearby_safe'),

    # PWA & System
    path('manifest.json',                       views.pwa_manifest,         name='manifest'),
    path('sw.js',                               views.service_worker,       name='sw'),
    path('set-language/',                       views.set_language,         name='set_language'),
    path('import-crimes/',                      views.import_crimes,        name='import_crimes'),
    # MTech Advanced Features
    path('explainer/<int:area_id>/',     views.area_explainer,       name='explainer'),
    path('anomaly/<int:area_id>/',       views.anomaly_detection,    name='anomaly'),
    path('yoy-analysis/',               views.yoy_analysis,         name='yoy_analysis'),
    path('clustering/',                 views.crime_clustering,     name='clustering'),
    path('stats-test/',                 views.statistical_test,     name='stats_test'),
    path('2fa/setup/',                  views.setup_2fa,            name='setup_2fa'),
    path('2fa/verify/',                 views.verify_2fa,           name='verify_2fa'),
    path('2fa/disable/',                views.disable_2fa,          name='disable_2fa'),

]
