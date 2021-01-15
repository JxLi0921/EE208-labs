class Cache:
    def __init__(self, capacity = 100):
        self.time_stamp = 0         # 当前的“时间”
        self.data = {}              # 一个记录key对应的搜索结果和最近使用时间的dict
        self.capacity = capacity    # 最大容量

    def remove_least_used(self):
        '''
            当Cache满了的时候，删除最近使用时间最小的(即最久没用过的)
        '''
        min_time_stamp = 19260817810  # 初始化时间为一个较大的数
        m_key = None                  # 对应地key初始化为None

        for key, value in self.data.keys(): # 寻找最久没用过的key
            if value[1] < min_time_stamp:
                min_time_stamp = value[1]
                m_key = key       
        
        del self.data[m_key]          # 在cache中删除这个key

    
    def add(self, key, value):
        self.time_stamp += 1                     # 时间流逝
        if len(self.data) == self.capacity:      # 如果满了，就删除一部分
            self.remove_least_used()
        self.data[key] = value, self.time_stamp  # 更新最近使用时间


    def find(self, key):
        self.time_stamp += 1                     # 时间流逝
        if key in self.data:                     # 存在key，更新最近使用时间并返回对应的搜索结果
            v, _ = self.data[key]
            self.data[key] = v, self.time_stamp
            return v
        return None                              # 不存在key，返回None
