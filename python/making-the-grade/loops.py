"""Functions for organizing and calculating student exam scores."""


PASSING_SCORE = 40
PERFECT_SCORE = 100


def round_scores(student_scores):
    """Round all provided student scores.

    Parameters:
        student_scores (list[float]): Student exam scores.

    Returns:
        list[int]: Student scores *rounded* to the nearest integer value.
    """

    rounded_scores = []
    for score in list(student_scores):
        rounded_scores.append(round(score))
    return rounded_scores


def count_failed_students(student_scores):
    """Count the number of failing students out of the group provided.

    Parameters:
        student_scores (list[int]): Student scores as ints.

    Returns:
        int: The count of student scores at or below 40.
    """

    failed_students = 0
    for score in student_scores:
        if score <= PASSING_SCORE:
            failed_students += 1
    return failed_students


def above_threshold(student_scores, threshold):
    """Determine how many of the provided student scores were 'the best' based on the provided threshold.

    Parameters:
        student_scores (list[int]): Integer scores.
        threshold (int): The threshold to cross to be the "best" score.

    Returns:
        list[int]: Integer scores that are at or above the "best" threshold.
    """

    above_threshold_scores = []
    for score in student_scores:
        if score >= threshold:
            above_threshold_scores.append(score)
    return above_threshold_scores


def letter_grades(highest):
    """Create a list of grade thresholds based on the provided highest grade.

    Parameters:
        highest (int): The value of the highest exam score.

    Returns:
        list[int]: Lower threshold scores for each D-A letter grade interval.

        For example, where the highest score is 100, and failing is <= 40,
        The result would be [41, 56, 71, 86]:
            41 <= "D" <= 55
            56 <= "C" <= 70
            71 <= "B" <= 85
            86 <= "A" <= 100
    """

    increment = (highest - PASSING_SCORE) // 4
    grades_thresholds = []
    for threshold in range(PASSING_SCORE +1, highest, increment):
        grades_thresholds.append(threshold)
    return grades_thresholds


def student_ranking(student_scores, student_names):
    """Organize the student's rank, name, and grade information in descending order.

    Parameters:
        student_scores (list): Scores in descending order.
        student_names (list[str]): Student names by exam score in descending order.

    Returns:
        list[str]: Strings in format ["<rank>. <student name>: <score>"].
    """

    ranking = []
    for index, name in enumerate(student_names):
        text = f"{index + 1}. {name}: {student_scores[index]}"
        ranking.append(text)
    return ranking


def perfect_score(student_info):
    """Create a list that contains the name and grade of the first student to make a perfect score on the exam.

    Parameters:
        student_info (list[list[str, int]]): List of [<student name>, <score>] lists.

    Returns:
        list: First `[<student name>, 100]` found OR `[]` if no student score of 100 is found.
    """

    for name, score in student_info:
        if score == PERFECT_SCORE:
            return [name, score]
    return []
