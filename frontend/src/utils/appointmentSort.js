export const sortAppointmentsByDate = (appointments) => (
  [...appointments].sort((first, second) => (
    new Date(first.appointment_datetime) - new Date(second.appointment_datetime)
  ))
);
