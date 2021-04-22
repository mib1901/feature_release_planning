class Feature:
    '''
    Features are flat, they do not have children, but they may depend on other features, 
    meaning that a feature can be implemented only after the feature(s) it depends on have
    been implemented and released
    ''' 

    def __init__(self, id:int, name:str, effort:float, cost:float, revenue:float, parents:list[int], children:list[int]):
        '''
        Creates a new feature \n
        Parameters:
            id : int - id of the feature
            name : str - name of the feature
            effort : float - effort to implement the feature in person days
            duration : float - duration to implement the feature
            cost : float - cost to implement the feature
            revenue : float - the annual revenue the feature brings once released in production
            depends_on : list[int] - list of feature ids that need to have been already implemented
            dependends : list[int] - list of feature ids that need this feature to have been implemented
        '''
        self.id = id
        self.name = name
        self.effort = effort                                # person days
        self.cost = cost                                    # overall cost to bring to production
        self.revenue = revenue                              # annual revenue once in production
        self.parents = parents
        self.children = children
        self.start:int = 0                                  # relative to start of plan
        self.end:int = 0                                    # relative to start of plan
        self.duration:int = 0                                # days
        self.avg_daily_effort:float = 0.0
        self.avg_daily_cost: float = 0.0
        self.avg_daily_revenue: float = self.revenue/240.0
        self.resources:list[int] = None


    def set_start_date(self, start:int, daily_effort:int):
        '''
        Set the start date and make the end date = start date + duration -1
        '''
        self.start = start
        self.duration = int(self.effort / daily_effort)
        if self.duration <=0:
            self.duration = 1
        self.end = self.start + self.duration-1
        self.avg_daily_effort = daily_effort
        self.avg_daily_cost = self.cost / self.duration

    def shift_dates(self, shift:int):
        '''
        Set the start date and make the end date = start date + duration -1
        '''
        self.start += shift
        self.end += shift

    def change_duration(self, daily_effort:int):
        self.duration = int(self.effort / daily_effort)
        self.end = self.start + self.duration -1