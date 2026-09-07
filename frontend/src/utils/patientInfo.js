export const calculateAge = (dateOfBirth, referenceDate = new Date()) => {
  if (!dateOfBirth) return null;
  const [year, month, day] = String(dateOfBirth).slice(0, 10).split('-').map(Number);
  if (!year || !month || !day) return null;

  let age = referenceDate.getFullYear() - year;
  const birthdayNotReached = referenceDate.getMonth() + 1 < month
    || (referenceDate.getMonth() + 1 === month && referenceDate.getDate() < day);
  if (birthdayNotReached) age -= 1;
  return age >= 0 ? age : null;
};

export const ageLabel = (dateOfBirth, referenceDate = new Date()) => {
  const age = calculateAge(dateOfBirth, referenceDate);
  return age === null ? 'Idade não informada' : `${age} ${age === 1 ? 'ano' : 'anos'}`;
};
