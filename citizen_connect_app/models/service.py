from dataclasses import dataclass, asdict



@dataclass
class Service:
    id: str
    title: str
    description: str

   

    location: dict
    cost_model: str
    cost_details: float
    sponsorship_information: str
    availability_status: str
    service_channel: str
    service_status: str

    creation: str
    eligibility_condition: str
    rating: float

    ngo_id: str
    ngo_name: str

    service_category: dict

    def to_dict(self):
        return asdict(self)