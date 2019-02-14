from pkg_resources import resource_string

from auditor.agent import Agent
from auditor.trainers.site_visitor import SiteVisitor


def apply_male_treatment(agent: Agent, count=1):
    agent.add_treatment("gender", "male")
    for i in range(count):
        sites = resource_string('auditor.resources.qc_sites.gender', 'male.txt').decode('utf-8')
        sites = [x.strip() for x in sites.splitlines()]
        agent.training_steps.append(SiteVisitor(sites))
    return agent


def apply_female_treatment(agent: Agent, count=1):
    agent.add_treatment("gender", "female")
    for i in range(count):
        sites = resource_string('auditor.resources.qc_sites.gender', 'female.txt').decode('utf-8')
        sites = [x.strip() for x in sites.splitlines()]
        agent.training_steps.append(SiteVisitor(sites))
    return agent
