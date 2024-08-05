from odoo import http
from odoo.http import request, Response
import json
from datetime import datetime, timedelta

class OpSessionController(http.Controller):

    # @http.route('/api/sessions', type='json', auth='user')
    # def get_user_sessions(self):
    #     user = request.env.user
    #     student = request.env['op.student'].sudo().search([('user_id', '=', user.id)], limit=1)

    #     if not student:
    #         return Response(json.dumps({"error": "Student not found"}), status=404, mimetype='application/json')


    #     student_course = request.env['op.student.course'].sudo().search([('student_id', '=', student.id)], limit=1)
    #     if not student_course:
    #         return Response(json.dumps({"error": "Student course details not found"}), status=404, mimetype='application/json')

    #     batch_id = student_course.batch_id.id

    #     if not batch_id:
    #         return {
    #             'status': 'error',
    #             'message': 'User is not associated with any batch.'
    #         }

    #     sessions = request.env['op.session'].sudo().search([('batch_id', '=', batch_id)])
    #     sessions_data = []
    #     for session in sessions:
    #         sessions_data.append({
    #             'name': session.name,
    #             'start_datetime': session.start_datetime,
    #             'end_datetime': session.end_datetime,
    #             'course': session.course_id.name,
    #             'faculty': session.faculty_id.name,
    #             'subject': session.subject_id.name,
    #             'classroom': session.classroom_id.name,
    #             'state': session.state,
    #         })

    #     return {
    #         'status': 'success',
    #         'data': sessions_data
    #     }


    # @http.route('/api/sessions_parent', type='json', auth='user')
    # def get_parent_sessions(self):
    #     user = request.env.user
    #     parent = request.env['op.parent'].sudo().search([('user_id', '=', user.id)], limit=1)

    #     if not parent:
    #         return Response(json.dumps({"error": "Parent not found"}), status=404, mimetype='application/json')

    #     students = parent.student_ids

    #     if not students:
    #         return Response(json.dumps({"error": "No students found for this parent"}), status=404, mimetype='application/json')

    #     batch_ids = []
    #     for student in students:
    #         student_course = request.env['op.student.course'].sudo().search([('student_id', '=', student.id)], limit=1)
    #         if student_course:
    #             batch_ids.append(student_course.batch_id.id)

    #     if not batch_ids:
    #         return {
    #             'status': 'error',
    #             'message': 'None of the students are associated with any batch.'
    #         }

    #     sessions_data = []
    #     for batch_id in batch_ids:
    #         sessions = request.env['op.session'].sudo().search([('batch_id', '=', batch_id)])
    #         for session in sessions:
    #             sessions_data.append({
    #                 'name': session.name,
    #                 'start_datetime': session.start_datetime,
    #                 'end_datetime': session.end_datetime,
    #                 'course': session.course_id.name,
    #                 'faculty': session.faculty_id.name,
    #                 'subject': session.subject_id.name,
    #                 'classroom': session.classroom_id.name,
    #                 'state': session.state,
    #             })

    #     return {
    #         'status': 'success',
    #         'data': sessions_data
    #     }


    # @http.route('/api/sessions', type='http', auth='user', methods=['GET'])
    # def get_user_sessions(self):
    #     user = request.env.user
    #     student = request.env['op.student'].sudo().search([('user_id', '=', user.id)], limit=1)

    #     if not student:
    #         return Response(json.dumps({"error": "Student not found"}), status=404, mimetype='application/json')

    #     student_course = request.env['op.student.course'].sudo().search([('student_id', '=', student.id)], limit=1)
    #     if not student_course:
    #         return Response(json.dumps({"error": "Student course details not found"}), status=404, mimetype='application/json')

    #     batch_id = student_course.batch_id.id

    #     if not batch_id:
    #         return Response(json.dumps({
    #             'status': 'error',
    #             'message': 'User is not associated with any batch.'
    #         }), status=400, mimetype='application/json')

    #     sessions = request.env['op.session'].sudo().search([
    #         ('batch_id', '=', batch_id),
    #         # ('state', 'in', ['confirm', 'done'])
    #     ])
    #     sessions_data = []
    #     for session in sessions:
    #         sessions_data.append({
    #             'name': session.name,
    #             'start_datetime': session.start_datetime.isoformat() if session.start_datetime else None,
    #             'end_datetime': session.end_datetime.isoformat() if session.end_datetime else None,
    #             'course': session.course_id.name,
    #             'faculty': session.faculty_id.name,
    #             'subject': session.subject_id.name,
    #             'batch':session.batch_id.name,
    #             'classroom': session.classroom_id.name,
    #             'state': session.state,
    #         })

    #     return Response(json.dumps({
    #         'status': 'success',
    #         'data': sessions_data
    #     }), mimetype='application/json')

    @http.route('/api/sessions', type='http', auth='user', methods=['GET'])
    def get_user_sessions(self):
        user = request.env.user
        student = request.env['op.student'].sudo().search([('user_id', '=', user.id)], limit=1)

        if not student:
            return Response(json.dumps({"error": "Student not found"}), status=404, mimetype='application/json')

        student_course = request.env['op.student.course'].sudo().search([('student_id', '=', student.id)], limit=1)
        if not student_course:
            return Response(json.dumps({"error": "Student course details not found"}), status=404, mimetype='application/json')

        batch_id = student_course.batch_id.id

        if not batch_id:
            return Response(json.dumps({
                'status': 'error',
                'message': 'User is not associated with any batch.'
            }), status=400, mimetype='application/json')

        sessions = request.env['op.session'].sudo().search([
            ('batch_id', '=', batch_id),
            # ('state', 'in', ['confirm', 'done'])
        ])
        sessions_data = []
        for session in sessions:
            # Get timing details
            timing = session.timing_id

            if timing.am_pm == 'pm' and timing.hour != '12':
                start_hour = int(timing.hour) + 12
            else:
                start_hour = int(timing.hour)

            start_minute = int(timing.minute)
            start_datetime = datetime.combine(session.start_datetime.date(), datetime.min.time())
            start_datetime = start_datetime.replace(hour=start_hour, minute=start_minute)

            end_datetime = start_datetime + timedelta(hours=timing.duration)

            sessions_data.append({
                'name': session.name,
                'start_datetime': start_datetime.isoformat(),
                'end_datetime': end_datetime.isoformat(),
                'course': session.course_id.name,
                'faculty': session.faculty_id.name,
                'subject': session.subject_id.name,
                'batch': session.batch_id.name,
                'classroom': session.classroom_id.name,
                'state': session.state,
            })

        return Response(json.dumps({
            'status': 'success',
            'data': sessions_data
        }), mimetype='application/json')



    # @http.route('/api/sessions_parent', type='http', auth='user', methods=['GET'])
    # def get_parent_sessions(self):
    #     user = request.env.user
    #     parent = request.env['op.parent'].sudo().search([('user_id', '=', user.id)], limit=1)

    #     if not parent:
    #         return Response(json.dumps({"error": "Parent not found"}), status=404, mimetype='application/json')

    #     students = parent.student_ids

    #     if not students:
    #         return Response(json.dumps({"error": "No students found for this parent"}), status=404, mimetype='application/json')

    #     sessions_data = []
    #     for student in students:
    #         student_course = request.env['op.student.course'].sudo().search([('student_id', '=', student.id)], limit=1)
    #         if student_course:
    #             batch_id = student_course.batch_id.id
    #             sessions = request.env['op.session'].sudo().search([
    #                 ('batch_id', '=', batch_id),
    #                 # ('state', 'in', ['confirm', 'done'])
    #             ])
    #             for session in sessions:
    #                 sessions_data.append({
    #                     'name': session.name,
    #                     'start_datetime': session.start_datetime.isoformat() if session.start_datetime else None,
    #                     'end_datetime': session.end_datetime.isoformat() if session.end_datetime else None,
    #                     'course': session.course_id.name,
    #                     'faculty': session.faculty_id.name,
    #                     'subject': session.subject_id.name,
    #                     'batch': session.batch_id.name,
    #                     'classroom': session.classroom_id.name,
    #                     'state': session.state,
    #                     'student_name': student.name  # Menambahkan nama anak
    #                 })

    #     return Response(json.dumps({
    #         'status': 'success',
    #         'data': sessions_data
    #     }), mimetype='application/json')

    @http.route('/api/sessions_parent', type='http', auth='user', methods=['GET'])
    def get_parent_sessions(self):
        user = request.env.user
        parent = request.env['op.parent'].sudo().search([('user_id', '=', user.id)], limit=1)

        if not parent:
            return Response(json.dumps({"error": "Parent not found"}), status=404, mimetype='application/json')

        students = parent.student_ids

        if not students:
            return Response(json.dumps({"error": "No students found for this parent"}), status=404, mimetype='application/json')

        sessions_data = []
        for student in students:
            student_course = request.env['op.student.course'].sudo().search([('student_id', '=', student.id)], limit=1)
            if student_course:
                batch_id = student_course.batch_id.id
                sessions = request.env['op.session'].sudo().search([
                    ('batch_id', '=', batch_id),
                    # ('state', 'in', ['confirm', 'done'])
                ])
                for session in sessions:
                    # Get timing details
                    timing = session.timing_id

                    if timing.am_pm == 'pm' and timing.hour != '12':
                        start_hour = int(timing.hour) + 12
                    else:
                        start_hour = int(timing.hour)

                    start_minute = int(timing.minute)
                    start_datetime = datetime.combine(session.start_datetime.date(), datetime.min.time())
                    start_datetime = start_datetime.replace(hour=start_hour, minute=start_minute)

                    # Calculate end datetime based on duration
                    end_datetime = start_datetime + timedelta(hours=timing.duration)

                    sessions_data.append({
                        'name': session.name,
                        'start_datetime': start_datetime.isoformat(),
                        'end_datetime': end_datetime.isoformat(),
                        'course': session.course_id.name,
                        'faculty': session.faculty_id.name,
                        'subject': session.subject_id.name,
                        'batch': session.batch_id.name,
                        'classroom': session.classroom_id.name,
                        'state': session.state,
                        'student_name': student.name
                    })

        return Response(json.dumps({
            'status': 'success',
            'data': sessions_data
        }), mimetype='application/json')

