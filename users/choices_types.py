class ProfileRoles:
    SUPERUSER = 1
    ADMINISTRATOR = 2
    CURATOR = 3
    LEARNER = 4

    CHOICES = [
        (SUPERUSER, 'Main administrator'),
        (ADMINISTRATOR, 'Administrator'),
        (CURATOR, 'Curator'),
        (LEARNER, 'Learner'),
    ]


class TaskStatus:
    NEW = 1
    REVIEW = 2
    EDIT = 3
    ACCEPT = 4

    CHOICES = [
        (1, 'New lesson'),
        (2, 'On review'),
        (3, 'Need edit task'),
        (4, 'Accepted'),
    ]
