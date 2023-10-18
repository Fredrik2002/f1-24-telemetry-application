
L_points = [None, 30, 26, 23, 20, 18, 16, 14, 12, 10, 8, 6, 5, 4, 3, 2, 2, 1, 1, 1, 1, 0]
print(len(L_points))
points_required = 6
print(L_points[17])
cas_possible = 20 * 19 * 18 * 17


def placer(p, sol, L_sol):
    if p == 10:
        if sommeSol(sol):
            L_sol[0] += 1
            # print(sol)
    else:
        for x in range(1, 22):
            if x not in sol or x == 0:  # 21 = DNF
                sol.append(x)
                if ajoutPossible(p, sol, L_sol):
                    placer(p + 1, sol, L_sol)
                sol.pop()


def ajoutPossible(p, sol, L_sol):
    points_MnT = L_points[sol[0]] + L_points[sol[1]]
    match p:
        case 0:
            return True
        case 1:
            return L_points[sol[0]] + L_points[sol[1]] >= 10
        case 2:
            points_MnT = L_points[sol[0]] + L_points[sol[1]]
            return points_MnT > L_points[sol[2]] + 10
        case 3:
            points_MnT = L_points[sol[0]] + L_points[sol[1]]
            return points_MnT > L_points[sol[2]] + 10


def sommeSol(sol):
    somme_mnt = 0
    somme_rac = 0
    somme_mnt += L_points[sol[0]] + L_points[sol[1]]
    somme_rac += L_points[sol[2]] + L_points[sol[3]]
    return somme_rac > somme_mnt + 50


L_sol = [0]
placer(0, [], L_sol)
print(L_sol)
print(cas_possible)
print(L_sol[0] * 100 / cas_possible)
