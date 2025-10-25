from collections import deque, defaultdict

def uav_bandwidth(B, phi, t):
    t_mod = (t + phi) % 10
    if t_mod in [0, 1, 8, 9]:
        return 0.0
    elif t_mod in [2, 7]:
        return B / 2
    else:
        return B

class UAVNetwork:
    def __init__(self, M, N, uav_info, flows, T=50, debug=False):
        self.M = M
        self.N = N
        self.T = T
        self.debug = debug

        self.B = [[0 for _ in range(N)] for _ in range(M)]
        self.phi = [[0 for _ in range(N)] for _ in range(M)]
        for x, y, B_val, phi_val in uav_info:
            self.B[x][y] = B_val
            self.phi[x][y] = phi_val

        self.flows = []
        for f in flows:
            region_raw = (f[5], f[6], f[7], f[8])
            region = self._normalize_region(region_raw)
            flow_dict = {
                'id': f[0],
                'pos': (f[1], f[2]),
                't_start': f[3],
                'size': f[4],
                'remaining': f[4],
                'region': region,
                'schedule': [],
                'hops': 0,
                'landing_changes': 0
            }
            self.flows.append(flow_dict)

        # self.validate_inputs()

    def _normalize_region(self, region):
        m1, n1, m2, n2 = region
        m1, m2 = min(m1, m2), max(m1, m2)
        n1, n2 = min(n1, n2), max(n1, n2)

        m1 = max(0, min(self.M - 1, m1))
        m2 = max(0, min(self.M - 1, m2))
        n1 = max(0, min(self.N - 1, n1))
        n2 = max(0, min(self.N - 1, n2))
        return (m1, n1, m2, n2)

    def _dist_to_region(self, pos, region):
        x, y = pos
        m1, n1, m2, n2 = region
        dx = 0 if m1 <= x <= m2 else min(abs(x - m1), abs(x - m2))
        dy = 0 if n1 <= y <= n2 else min(abs(y - n1), abs(y - n2))
        return dx + dy

    # def validate_inputs(self):

    #     for f in self.flows:
    #         d = self._dist_to_region(f['pos'], f['region'])
    #         if f['t_start'] + d >= self.T:
    #             if self.debug:
    #                 print(f"[WARN] Flow {f['id']} nie zdąży dotrzeć do regionu w T={self.T} (t_start={f['t_start']}, dist={d}).")

    #     pos_Bpos = np.sum(self.B > 0)
    #     if pos_Bpos == 0 and self.debug:
    #         print("[WARN] Brak dronów z dodatnią bazową przepustowością B.")

    def shortest_path_to_region(self, start, region):
        m1, n1, m2, n2 = region
        visited = [[False for _ in range(self.N)] for _ in range(self.M)]
        parent = dict()
        queue = deque()
        queue.append(start)
        visited[start[0]][start[1]] = True

        while queue:
            x, y = queue.popleft()
            if m1 <= x <= m2 and n1 <= y <= n2:
                path = []
                cx, cy = x, y
                while (cx, cy) != start:
                    path.append((cx, cy))
                    cx, cy = parent[(cx, cy)]
                path.reverse()
                return path
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.M and 0 <= ny < self.N and not visited[nx][ny]:
                    visited[nx][ny] = True
                    parent[(nx, ny)] = (x, y)
                    queue.append((nx, ny))
        return []

    def UAVsearch(self, flow, occupancy):
        x, y = flow['pos']
        return (x, y)

    def neighbors_in_region(self, pos, region):
        x, y = pos
        m1, n1, m2, n2 = region
        neigh = [(x, y), (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        res = []
        for cx, cy in neigh:
            if 0 <= cx < self.M and 0 <= cy < self.N:
                if m1 <= cx <= m2 and n1 <= cy <= n2:
                    res.append((cx, cy))
        return res

    def current_cell_for_flow(self, flow, t):
        if '_last_cell' in flow:
            return flow['_last_cell']
        path = flow.get('path', [])
        if not path:
            return flow.get('final_uav', flow['pos'])
        idx = max(0, t - flow['t_start'])
        if idx < len(path):
            return path[idx]
        else:
            return flow['final_uav']

    def schedule_flows_v2(self):

        for flow in self.flows:
            flow['path'] = self.shortest_path_to_region(flow['pos'], flow['region'])
            flow['final_uav'] = flow['path'][-1] if flow['path'] else flow['pos']

        for t in range(self.T):
            active = [f for f in self.flows if f['remaining'] > 0 and t >= f['t_start']]
            if not active:
                continue

            cur_pos = {f['id']: self.current_cell_for_flow(f, t) for f in active}

            Bt = {}
            for x in range(self.M):
                for y in range(self.N):
                    Bt[(x, y)] = uav_bandwidth(self.B[x][y], self.phi[x][y], t)

            candidates = {f['id']: self.neighbors_in_region(cur_pos[f['id']], f['region']) for f in active}

            if self.debug and t % 10 == 0:
                total_B = sum(Bt.values())
                active_with_cands = sum(1 for f in active if len(candidates[f['id']]) > 0)
                print(f"[t={t}] active={len(active)}, active_with_cands={active_with_cands}, total_B={total_B:.2f}")

            small_first = sorted(active, key=lambda f: f['remaining'])
            residual_Bt = dict(Bt)
            pinned_assign = {}
            pinned_reserved = {}
            pinned_by_cell = defaultdict(list)

            for f in small_first:
                fid = f['id']
                rem = f['remaining']
                if rem <= 0:
                    continue
                cands = [c for c in candidates[fid] if residual_Bt.get(c, 0.0) >= rem]
                if not cands:
                    continue

                def tie_key(cell):
                    stay_pref = 0 if cell == cur_pos[fid] else 1
                    dist = abs(cell[0] - cur_pos[fid][0]) + abs(cell[1] - cur_pos[fid][1])
                    return (residual_Bt[cell], stay_pref, dist, cell[0], cell[1])

                chosen = min(cands, key=tie_key)
                pinned_assign[fid] = chosen
                pinned_reserved[fid] = rem
                pinned_by_cell[chosen].append(fid)
                residual_Bt[chosen] = max(0.0, residual_Bt[chosen] - rem)

            rest = [f for f in active if f['id'] not in pinned_assign]
            assign2 = {}

            for f in rest:
                fid = f['id']
                cands = candidates[fid]
                if not cands:
                    assign2[fid] = None
                else:
                    def init_key(cell):
                        stay_pref = 0 if cell == cur_pos[fid] else 1
                        dist = abs(cell[0] - cur_pos[fid][0]) + abs(cell[1] - cur_pos[fid][1])
                        return (-residual_Bt[cell], stay_pref, dist, cell[0], cell[1])
                    assign2[fid] = max(cands, key=init_key)

            max_iters = 10
            for _ in range(max_iters):
                occ = defaultdict(int)
                for fid, cell in assign2.items():
                    if cell is not None:
                        occ[cell] += 1

                changed = False
                for f in rest:
                    fid = f['id']
                    cands = candidates[fid]
                    cur = assign2[fid]

                    def eff_share(cell):
                        if cell is None:
                            return 0.0
                        add = 0 if cur == cell else 1
                        denom = max(1, occ[cell] + add)
                        return residual_Bt[cell] / denom

                    if not cands:
                        best_cell = None
                    else:
                        best_val = -1.0
                        best_cell = cur
                        for cell in cands:
                            val = eff_share(cell)
                            if val > best_val:
                                best_val = val
                                best_cell = cell
                            elif abs(val - best_val) < 1e-12:
                                prefer_stay_new = 0 if cell == cur else 1
                                prefer_stay_best = 0 if best_cell == cur else 1
                                if prefer_stay_new < prefer_stay_best:
                                    best_cell = cell
                                elif prefer_stay_new == prefer_stay_best:
                                    if residual_Bt[cell] > residual_Bt.get(best_cell, -1e18):
                                        best_cell = cell
                                    elif abs(residual_Bt[cell] - residual_Bt.get(best_cell, -1e18)) < 1e-12:
                                        dist_new = abs(cell[0] - cur_pos[fid][0]) + abs(cell[1] - cur_pos[fid][1])
                                        dist_best = abs(best_cell[0] - cur_pos[fid][0]) + abs(best_cell[1] - cur_pos[fid][1])
                                        if dist_new < dist_best or (dist_new == dist_best and cell < best_cell):
                                            best_cell = cell

                    if best_cell != cur:
                        if cur is not None:
                            occ[cur] -= 1
                        if best_cell is not None:
                            occ[best_cell] += 1
                        assign2[fid] = best_cell
                        changed = True

                if not changed:
                    break

            reserved_sum_by_cell = defaultdict(float)
            for fid, cell in pinned_assign.items():
                reserved_sum_by_cell[cell] += pinned_reserved[fid]

            flows_p1_by_cell = defaultdict(list)
            for fid, cell in pinned_assign.items():
                flows_p1_by_cell[cell].append(fid)

            flows_p2_by_cell = defaultdict(list)
            for fid, cell in assign2.items():
                if cell is not None:
                    flows_p2_by_cell[cell].append(fid)

            for cell, fids in flows_p1_by_cell.items():
                x, y = cell
                for fid in fids:
                    f = next(fl for fl in active if fl['id'] == fid)
                    send = min(f['remaining'], pinned_reserved[fid])
                    if send > 0:
                        f['remaining'] -= send
                        f['schedule'].append((t, x, y, send))
                        f['_last_cell'] = cell

            for cell, fids in flows_p2_by_cell.items():
                x, y = cell
                total = Bt[cell]
                rem_after_p1 = max(0.0, total - reserved_sum_by_cell[cell])
                if rem_after_p1 <= 0 or not fids:
                    continue
                share = rem_after_p1 / len(fids)
                for fid in fids:
                    f = next(fl for fl in active if fl['id'] == fid)
                    send = min(f['remaining'], share)
                    if send > 0:
                        f['remaining'] -= send
                        f['schedule'].append((t, x, y, send))
                    f['_last_cell'] = cell

    def schedule_flows(self):
        return self.schedule_flows_v2()

    def compute_score(self):
        scores = []
        for flow in self.flows:
            schedule = flow['schedule']
            if not schedule:
                scores.append((flow['id'], 0))
                continue

            total_sent = sum(z for _, _, _, z in schedule)
            traffic_score = total_sent / flow['size'] if flow['size'] > 0 else 0.0

            positive = [t for t, _, _, z in schedule if z > 0]
            last_time = max(positive) if positive else flow['t_start']
            delay_score = 1 - (last_time - flow['t_start']) / self.T
            delay_score = max(0, delay_score)

            distance_score = 2 ** (-(len(flow.get('path', []))))

            last_uav = None
            changes = 0
            for _, x, y, _ in schedule:
                current = (x, y)
                if last_uav is None:
                    last_uav = current
                elif current != last_uav:
                    changes += 1
                    last_uav = current
            landing_score = 1 / (1 + changes)

            flow_score = 100 * (0.4 * traffic_score + 0.2 * delay_score + 0.3 * distance_score + 0.1 * landing_score)
            scores.append((flow['id'], flow_score))
        return scores

    def print_and_return_schedule(self):
        schedule = []
        for flow in self.flows:
            p = len(flow['schedule'])
            print(flow['id'], p)
            schedule.append([flow['id'],p])
            for rec in flow['schedule']:
                t, x, y, z = rec
                print(t, x, y, z)
                schedule.append([t,x,y,z])
        return schedule
                
class UAVx:
    def __init__(self,x,y,B,fi):
        self.x = x
        self.y = y
        self.B = B
        self.fi = fi
        
    def b(self, t):
        t = (t + self.fi) % 10
        if t in [2,7]:
            return self.B
        elif t in [3,4,5,6]:
             return self.B/2
        else:
            return 0
 
class flowx:
    def __init__(self ,f , x, y, t, Qtotal, m1, n1, m2, n2):
        self.f = f
        self.x = x
        self.y = y
        self.t = t
        self.Qtotal = Qtotal
        self.Q = Qtotal
        self.m1 = m1
        self.n1 = n1
        self.m2 = m2
        self.n2 = n2
        
def MAIN_PROGRAM(input_file): 
    with open(str(input_file),"r") as file:
        file = file.readlines()
        
        header = map(int,(file.pop(0).rstrip()).split(sep=' '))
        ### ODCZYTANIE : SZEROKOŚCI SIATKI (M) WYSOKOSCI SIATKI (N), ILOSC FLOWOW DO OBSLUZENIA (FN), CZAS SYMULACJI (T) ###
        M, N, FN, T = header
        
        ## UTWORZENIE PUSTEJ SIATKI
        topology = [[0 for _ in range(M)] for _ in range(N)]
        
        ### TWORZENIE SIATKI PELNEJ UAV O WYMIARACH M X N (KAZDY KOORDYNAT TO ODDZIELNY OBIEKT KLASY UAV)
        for row_index in range(M*N):
            readed_uav = UAVx(*map(int,(file[row_index].rstrip()).split(sep=' ')))
            topology[readed_uav.y][readed_uav.x] = readed_uav
        
        ### PRINT KORDYNATOW SIATKI (TESTOWY)
        flows = []
        for row_index in range(M*N,len(file)):
            flows.append(flowx(*map(int,(file[row_index].rstrip()).split(sep=' '))))

        UAV_list = []
        for row in topology:
            for uav in row:
                UAV_list.append([uav.x,uav.y,uav.B,uav.fi])
        uav_info = sorted(UAV_list, key=lambda e: (e[0], e[1]))
        
        flows = [[f.f,f.x,f.y,f.t,f.Qtotal,f.Q,f.m1,f.n1,f.m2,f.n2] for f in flows]
        
    network = UAVNetwork(M, N, UAV_list, flows, T)
    network.schedule_flows()
    return network.print_and_return_schedule()