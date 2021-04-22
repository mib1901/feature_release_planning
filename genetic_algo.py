
import matplotlib.pyplot as plt
import numpy as np
import random
import copy
import datetime
import gantt
from feature import Feature
from plan import Plan
import matplotlib.pyplot as plt


def mutate(plan: Plan):
    ndx = random.randrange(1, 1 + len(plan.features.items()))
    feature = plan.features.get(ndx)
    plan.schedule_feature(ndx, feature.start, feature.avg_daily_effort +1)
    plan.remove_idle_time()
    plan.update_derived()
    plan.score()


def cross_over(plan_a: Plan, plan_b: Plan):
    '''
    Chooses a cross-over and sets the feature start/end values accordingly
    '''
    ndx = random.randrange(0, len(plan_a.features.keys()))
    temp_dict = copy.deepcopy(plan_b.features)
    for i in range(1, ndx):
        plan_b.features[i].set_start_date(plan_a.features[i].start, plan_a.features[i].avg_daily_effort)
        plan_a.features[i].set_start_date(temp_dict[i].start, temp_dict[i].avg_daily_effort)
    plan_a.remove_idle_time()
    plan_b.remove_idle_time()
    plan_a.update_derived()
    plan_b.update_derived()
    plan_a.score()
    plan_b.score()
    return


def first_generation(pop_size: int, features: dict, plans:list[Plan]):
    for i in range(pop_size):
        plan = Plan(i, 'Plan {}'.format(i), 5, 24, 65, 0.05, copy.deepcopy(features))
        plans.append(plan)
    return

def run_ga(features:list[Feature], n_pop:int, n_gen:int)->Plan:
    plans: list[Plan] = []
    best_plans: list[Plan] = []
    first_generation(n_pop, features, plans)
    plans.sort(reverse=True)
    for ndx_gen in range(1, n_gen):
        temp_plans = copy.deepcopy(plans)
        for ndx_plan in range(2, int(n_pop/5)):
            plan = plans[ndx_plan]
            mutate(plan)
        for ndx_plan in range(int(n_pop/5)+1, int(2*n_pop/5), 2):
            plan_a = temp_plans[random.randrange(0, n_pop/4)]
            plan_b = temp_plans[random.randrange(0, n_pop/4)]
            cross_over(plan_a, plan_b)
            plans[ndx_plan] = plan_a
            plans[ndx_plan + 1] = plan_b
        for ndx_plan in range(int(2*n_pop/5)+1, n_pop):
            plans[ndx_plan].schedule()
        plans.sort(reverse=True)
        print("Generation: {}, NPV: {:.2f}".format(ndx_gen, plans[0].fitness_score))
        best_plans.append(plans[0])
        if ndx_gen >= 25 and plans[0].fitness_score > 0 and best_plans[-1].fitness_score == plans[0].fitness_score and best_plans[-2].fitness_score == best_plans[-1].fitness_score:
            break
    
    return plans[0]


def plot_gantt(plan:Plan):
    fig, ax_gnt = plt.subplots(figsize = (12, 6))

    # Add bars for each duration
    for k, feature in plan.features.items():
        ax_gnt.broken_barh([(feature.start, feature.duration)], (100-10*k, 8), facecolors = ('tab:red')) 
    
    ax_gnt.grid(True)
    ax_gnt.set_yticks([100-10*k+5 for k,f in plan.features.items()]) 
    ax_gnt.set_yticklabels([f.name for k,f in plan.features.items()]) 

    # Format the x-axis
    plt.show()
    return

def plot_effort(plan:Plan):
    plt.rcdefaults()
    y_pos = np.arange(len(best_plan.daily_effort))
    plt.bar(y_pos, best_plan.daily_effort, align='center', alpha=0.5)
    plt.ylabel('Daily effort')
    plt.title('Distribution of daily effort')
    plt.show()

if __name__ == "__main__":
    fs1 = {
        1: Feature(1, 'One  ', 30, 3000, 10000, None, [5]),
        2: Feature(2, 'Two  ', 60, 6000, 24000, None, [3, 6]),
        3: Feature(3, 'Three', 90, 9000, 10000, [2], [4]),
        4: Feature(4, 'Four ', 40, 4000, 25000, [3], None),
        5: Feature(5, 'Five', 90, 9000, 50000, [1], [4]),
        6: Feature(6, 'Six ', 60, 6000, 10000, [2], [4])}


    best_plan = run_ga(fs1, 500,500)
    features = best_plan.features
    print("\n")
    print(str(best_plan))
    for k, feature in features.items():
        print("Feature id: {}, Start: {}, End: {}, Average effort: {}".format(feature.id, feature.start, feature.end, feature.avg_daily_effort))

    plot_gantt(best_plan)
    plot_effort(best_plan)

   
