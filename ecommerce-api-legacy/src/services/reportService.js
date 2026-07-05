// Relatório financeiro. Reescrito com async/await + agregação em memória,
// eliminando o "callback hell" com contadores manuais de pendências (finding H4)
// e a explosão de queries N+1 (finding M1 / playbook P7): agora são 4 queries
// no total, independentemente do número de cursos/matrículas.
class ReportService {
    constructor({ courseModel, enrollmentModel, userModel, paymentModel }) {
        this.courseModel = courseModel;
        this.enrollmentModel = enrollmentModel;
        this.userModel = userModel;
        this.paymentModel = paymentModel;
    }

    async financialReport() {
        const [courses, enrollments, users, payments] = await Promise.all([
            this.courseModel.findAll(),
            this.enrollmentModel.findAll(),
            this.userModel.findAll(),
            this.paymentModel.findAll(),
        ]);

        const usersById = new Map(users.map((u) => [u.id, u]));
        const paymentByEnrollment = new Map(payments.map((p) => [p.enrollment_id, p]));
        const enrollmentsByCourse = new Map();
        for (const enr of enrollments) {
            if (!enrollmentsByCourse.has(enr.course_id)) enrollmentsByCourse.set(enr.course_id, []);
            enrollmentsByCourse.get(enr.course_id).push(enr);
        }

        return courses.map((course) => {
            const courseData = { course: course.title, revenue: 0, students: [] };
            for (const enr of enrollmentsByCourse.get(course.id) || []) {
                const user = usersById.get(enr.user_id);
                const payment = paymentByEnrollment.get(enr.id);
                if (payment && payment.status === 'PAID') {
                    courseData.revenue += payment.amount;
                }
                courseData.students.push({
                    student: user ? user.name : 'Unknown',
                    paid: payment ? payment.amount : 0,
                });
            }
            return courseData;
        });
    }
}

module.exports = ReportService;
