from app.db.database import SessionLocal
from app.models.route import Route
from app.models.attraction import Attraction
from app.models.route_attraction import RouteAttraction

def seed_data():
    """导入初始数据"""
    db = SessionLocal()

    try:
        # 检查是否已有数据
        existing_routes = db.query(Route).count()
        if existing_routes > 0:
            print("数据库已有数据，跳过初始化")
            return

        # 路线1：郑州-洛阳历史文化线
        route1 = Route(
            name="郑州-洛阳历史文化之旅",
            description="探索中原文明的源头，游览河南两大古都，感受千年历史文化底蕴",
            region="郑州-洛阳",
            route_type="历史文化",
            duration="3-4天",
            difficulty="简单"
        )
        db.add(route1)
        db.flush()

        # 路线1的景点
        attractions_route1 = [
            Attraction(name="河南博物院", description="中国建立较早的博物馆之一，馆藏文物丰富",
                      address="郑州市金水区农业路8号", latitude=34.7985, longitude=113.6673),
            Attraction(name="黄河风景名胜区", description="黄河中下游分界线，观赏黄河壮丽景观",
                      address="郑州市惠济区邙山黄河南岸", latitude=34.8823, longitude=113.5956),
            Attraction(name="龙门石窟", description="中国四大石窟之一，世界文化遗产",
                      address="洛阳市洛龙区龙门中街13号", latitude=34.5542, longitude=112.4747),
            Attraction(name="白马寺", description="中国第一古刹，佛教传入中国后兴建的第一座官办寺院",
                      address="洛阳市洛龙区洛白路6号", latitude=34.7156, longitude=112.6089),
        ]

        for idx, attr in enumerate(attractions_route1):
            db.add(attr)
            db.flush()
            db.add(RouteAttraction(route_id=route1.id, attraction_id=attr.id, order=idx+1))

        # 路线2：云台山-太行山自然风光线
        route2 = Route(
            name="云台山-太行山自然风光之旅",
            description="领略太行山水之美，观赏云台山瀑布峡谷，体验大自然的鬼斧神工",
            region="焦作",
            route_type="自然风光",
            duration="2-3天",
            difficulty="中等"
        )
        db.add(route2)
        db.flush()

        attractions_route2 = [
            Attraction(name="云台山红石峡", description="云台山最美景区，峡谷丹霞地貌",
                      address="焦作市修武县云台山景区", latitude=35.4201, longitude=113.3627),
            Attraction(name="云台山潭瀑峡", description="三步一泉、五步一瀑、十步一潭",
                      address="焦作市修武县云台山景区", latitude=35.4215, longitude=113.3641),
            Attraction(name="茱萸峰", description="云台山主峰，登高望远观太行",
                      address="焦作市修武县云台山景区", latitude=35.4389, longitude=113.3712),
        ]

        for idx, attr in enumerate(attractions_route2):
            db.add(attr)
            db.flush()
            db.add(RouteAttraction(route_id=route2.id, attraction_id=attr.id, order=idx+1))

        # 路线3：开封古都文化线
        route3 = Route(
            name="开封古都文化探索",
            description="穿越千年宋都，感受清明上河图的繁华，品味开封独特的历史韵味",
            region="开封",
            route_type="历史文化",
            duration="2天",
            difficulty="简单"
        )
        db.add(route3)
        db.flush()

        attractions_route3 = [
            Attraction(name="清明上河园", description="大型宋代文化主题公园，再现清明上河图盛景",
                      address="开封市龙亭区龙亭西路5号", latitude=34.8223, longitude=114.3396),
            Attraction(name="开封府", description="北宋时期天下首府，包公办案所在地",
                      address="开封市鼓楼区包公东湖北岸", latitude=34.7976, longitude=114.3548),
            Attraction(name="大相国寺", description="中国著名佛教寺院，鲁智深倒拔垂杨柳的故事发生地",
                      address="开封市鼓楼区自由路西段36号", latitude=34.7912, longitude=114.3501),
        ]

        for idx, attr in enumerate(attractions_route3):
            db.add(attr)
            db.flush()
            db.add(RouteAttraction(route_id=route3.id, attraction_id=attr.id, order=idx+1))

        # 路线4：少林寺-嵩山禅武之旅
        route4 = Route(
            name="少林寺-嵩山禅武之旅",
            description="探访天下第一名刹少林寺，登临中岳嵩山，感受禅宗文化和武术精神",
            region="郑州-登封",
            route_type="文化体验",
            duration="2天",
            difficulty="中等"
        )
        db.add(route4)
        db.flush()

        attractions_route4 = [
            Attraction(name="少林寺", description="中国佛教禅宗祖庭和中国功夫发源地",
                      address="郑州市登封市嵩山少林寺", latitude=34.5089, longitude=112.9349),
            Attraction(name="塔林", description="少林寺历代高僧墓塔群，中国现存最大的塔林",
                      address="郑州市登封市少林寺西侧", latitude=34.5067, longitude=112.9312),
            Attraction(name="嵩山", description="五岳之一中岳嵩山，道教圣地",
                      address="郑州市登封市嵩山风景区", latitude=34.4853, longitude=113.0345),
        ]

        for idx, attr in enumerate(attractions_route4):
            db.add(attr)
            db.flush()
            db.add(RouteAttraction(route_id=route4.id, attraction_id=attr.id, order=idx+1))

        # 路线5：郑州城市文化游
        route5 = Route(
            name="郑州城市文化一日游",
            description="漫步现代都市郑州，探寻黄河文明，品味中原美食",
            region="郑州",
            route_type="城市休闲",
            duration="1天",
            difficulty="简单"
        )
        db.add(route5)
        db.flush()

        attractions_route5 = [
            Attraction(name="二七纪念塔", description="郑州地标建筑，纪念二七大罢工",
                      address="郑州市二七区二七广场", latitude=34.7510, longitude=113.6454),
            Attraction(name="郑州商城遗址", description="商代早期都城遗址，中国重点文物保护单位",
                      address="郑州市管城区商城路", latitude=34.7589, longitude=113.6712),
            Attraction(name="绿城广场", description="郑州市中心绿地广场，市民休闲好去处",
                      address="郑州市金水区金水路与中州大道交叉口", latitude=34.7634, longitude=113.6823),
        ]

        for idx, attr in enumerate(attractions_route5):
            db.add(attr)
            db.flush()
            db.add(RouteAttraction(route_id=route5.id, attraction_id=attr.id, order=idx+1))

        db.commit()
        print("初始数据导入成功！")
        print(f"共导入 {db.query(Route).count()} 条路线")
        print(f"共导入 {db.query(Attraction).count()} 个景点")

    except Exception as e:
        db.rollback()
        print(f"数据导入失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
