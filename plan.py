import random
import numpy as np 
import numpy_financial as npf
from datetime import date
from feature import Feature


class Plan:
    '''
    A Plan is a list of ordered features
    '''

    def __init__(self, id:int, name:str, effort_bandwidth:float, no_periods:int, period_duration:int, discont_rate:float, features:dict[int, Feature]):
        '''
        Create a new project \n
        Parameters:
            id : int - project id
            name : str - project's name
            effort_bandwidth : float - average effort bandwidth per
            no_periods : int - number of periods for which the cash flows are calculated 
        '''
        self.id = id
        self.name = name
        self.effort_bandwidth = effort_bandwidth
        self.in_bandwidth:bool = True
        self.no_periods = no_periods
        self.period_duration = period_duration
        self.discount_rate = discont_rate
        self.features = features
        self.meets_dependencies: bool = True
        self.start =int()
        self.end = int()
        self.duration = int()
        self.max_duration = int()
        self.effort = 0.0
        self.cost = 0.0
        self.value  = 0.0
        self.period_cost: np.ndarray = np.zeros(self.no_periods)
        self.period_revenue: np.ndarray = np.zeros(self.no_periods)
        self.period_cash_flow: np.ndarray = np.zeros(self.no_periods)
        self.fitness_score:float = 0
        self.daily_effort: np.ndarray = None
        self.daily_cash_flow: list[int] = None

        self.compute_max_duration()
        self.schedule()
        return
    

    def __lt__(self, other):
        return self.fitness_score < other.fitness_score

    def __le__(self, other):
        return self.fitness_score <= other.fitness_score
        
    def __eq__(self, other):
        return self.fitness_score == other.fitness_score

    def __str__(self):
        return "Plan id: {}, name: {}, start: {}, end: {}, score: {:.2f}".format(self.id, self.name, self.start, self.end, self.fitness_score)

    def compute_max_duration(self):
        '''
        Computes the duration of the project in days when all features are serialized
        '''
        self.max_duration = 0.0
        for k, feature in  self.features.items():
            self.max_duration += feature.effort
        return        
    
    def compute_duration(self):
        '''
        Computes the duration of the project in days
        '''
        self.duration = 0
        self.effort = 0
        self.cost = 0.0
        self.value = 0.0
        self.end = 0
        for k, feature in  self.features.items():
            if(self.end < feature.end):
                self.end = feature.end
            self.effort += feature.effort
            self.cost += feature.cost
            self.value += feature.revenue
        self.duration = self.end - self.start + 1
        return

    def compute_daily_effort(self):
        '''
        Compute the daily effort needs and checks if the dailty effort bandwidth is exceeded
        '''
        if self.duration > 0:
            self.daily_effort = np.zeros(int(self.duration))
            for i in range(0,int(self.duration)):
                for feature in self.features.values():
                    if(feature.start<=i and i<=feature.end):
                        self.daily_effort[i] += feature.avg_daily_effort
        if(self.daily_effort.max()> self.effort_bandwidth):
            self.in_bandwidth=False
        return

    def compute_cashflow(self):
        '''
        Compute cash flow (i) = value(i) - cost(i)
        '''
        cf_duration = self.period_duration*self.no_periods
        self.daily_cash_flow = np.zeros(cf_duration, dtype=float)

        for per in range(0,self.no_periods):
            period_cash_flow = 0
            for day in range(0, self.period_duration):
                cash_flow = 0.0
                i = per*self.period_duration + day
                for feature in self.features.values():
                    if(feature.start<=i<=feature.end):
                        cash_flow = cash_flow - feature.avg_daily_cost
                    if (feature.end < i):
                        cash_flow = cash_flow + feature.avg_daily_revenue
                    continue          
                self.daily_cash_flow[i] = cash_flow
                period_cash_flow += cash_flow
            self.period_cash_flow[per] = period_cash_flow
        return

    def score(self):
        '''
        Computes quarterly npv \n
        Parameters:
            discount_rate:float - annual discount rate absolute number, not %
        '''
        if(self.meets_dependencies == False):
            self.fitness_score = 0
        elif(self.in_bandwidth == False):
            self.fitness_score = 0.9 * npf.npv(self.discount_rate, self.period_cash_flow)
        else:
            self.fitness_score = npf.npv(self.discount_rate, self.period_cash_flow)
        return

    def schedule(self):
        if(random.randint(0,1)==0):
            self.schedule_random()
        else:
            self.schedule_linked()
        self.set_start_to_zero()
        self.update_derived()
        self.remove_idle_time()
        self.update_derived()
        self.score()
        return

    def schedule_random(self):
        '''
        Random schedule the features, without taking into account feature inter_dependencies. Updates duration, daily effort and cash flow
        '''
        for k, feature in self.features.items():
            feature.set_start_date(random.randrange(1, int(self.max_duration/2-feature.effort)), random.randrange(1,self.effort_bandwidth+1))
        return

    def schedule_linked(self):
        '''
        Random schedule root features, and taking into account feature inter_dependencies. Updates duration, daily effort and cash flow
        '''
        for k, feature in self.features.items():
            if feature.parents == None:
                feature.set_start_date(random.randrange(1, int(self.max_duration/2-feature.effort)), random.randrange(1,self.effort_bandwidth+1))
                if(feature.children != None):
                    self.schedule_children(feature)
        return

    def schedule_feature(self, feature_id:int, start:int, daily_effort:int):
        '''
        Schedule a feature and its children. Updates project duration and the dailty effort
        '''
        feature = self.features[feature_id]
        feature.set_start_date(start, daily_effort)
        self.update_derived()
        return

    def schedule_children(self, feature:Feature):
        for i in feature.children:
            child_feature = self.features[i]
            child_feature.set_start_date(feature.end+1, random.randrange(1,self.effort_bandwidth+1))
            if(child_feature.children != None):
                self.schedule_children(child_feature)
        return
    
    def set_start_to_zero(self):
        start = self.max_duration
        for k, feature in self.features.items():
            if(start > feature.start):            
                 start = feature.start                  

        for k, feature in self.features.items():
            feature.shift_dates(-start) 
        return

    def remove_idle_time(self):
        '''
        Removes idle time from the plan by shifting tasks with the amount of idle time
        '''
        idle_days  = [int]
        for i in range(0,len(self.daily_effort)):
            if self.daily_effort[i] == 0:
                idle_days.append(i)
        for i in range(len(idle_days)-1, 0, -1):
            for k, f in self.features.items():
                if f.start>idle_days[i]:
                    f.shift_dates(-1)


    def check_dependencies(self):
        for k, feature in self.features.items():
            children = feature.children
            if(children != None):
                for i_child in children:
                    if(feature.end > self.features.get(i_child).start):
                        self.meets_dependencies = False
                        break
        return                          
    
    def update_derived(self):
        '''
        Updates plan duration, daily effort and cash flow
        '''
        self.compute_duration()
        self.compute_daily_effort()
        self.compute_cashflow()
        self.check_dependencies()
        return
