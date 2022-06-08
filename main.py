"""
Vypracoval: Martin Hric
UI : Klastrovanie
FIIT STU
2021/2022
"""

import random
import math
import copy
import time
import matplotlib.pyplot as plt

all_points = []
INTERVAL = 5000
NUM_OF_POINTS = 20000

#vypocitanie euklidovskej vzdialenosti 2 bodov a,b
def euc_dist(a, b):
    return math.sqrt(((a[0] - b[0]) ** 2) + ((a[1] - b[1]) ** 2))

#vypocitanie priemernej vzdialenosti vsetkych bodov od hlavneho bodu v kazdom klastri
def calculate_avg(clusters):
    averages = []
    for cluster in clusters:
        distances = []
        for point in cluster["points"]:
            distances.append(euc_dist(point, cluster["main_point"]))
        averages.append(sum(distances) / len(cluster["points"]))

    return averages

#vyhodnotenie, ci klastrovanie bolo uspesne alebo nie
def result(clusters):
    averages = calculate_avg(clusters)
    global_average = round(sum(averages) / len(averages), 3)

    success = True
    for avg in averages:   #ak co i len 1 bod je dalej ako 500, ma to byt podla zadania ohodnotene ako neuspesne, co je trochu prisne, zvykol som to menit na 1000
        if avg >= 500:
            success = False
            break
    if success:
        print("Clustering successful")
    else:
        print("Clustering unsuccessful")
    print(f"Average distance in clusters: {global_average}")

    return global_average

# funkcia na vygenerovanie zadanych N bodov + 20 zaciatocnych bodov od ktorych su generovane v offsete +-100 , cize vygeneruje N + 20 bodov
def generate_points():
    points = {}
    first_20 = []
    for i in range(20):
        x = random.randint(-INTERVAL, INTERVAL)
        y = random.randint(-INTERVAL, INTERVAL)

        while (x, y) in points:
            x = random.randint(-INTERVAL, INTERVAL)
            y = random.randint(-INTERVAL, INTERVAL)

        points[(x, y)] = 0
        first_20.append((x, y))

    for i in range(NUM_OF_POINTS):
        point = random.choice(first_20)      #tato volba generovania offsetu nieje idealna, kedze 100 je dost male cisle, ja by som to osobne zvysil aspon na 1 000
        x_offset = random.randint(-1000,1000)  # navyse robi to stvorce a nie kruhy , to sa da vyriesit inou funckiou generovania, v zadani to bolo ale takto vysvetlene
        y_offset = random.randint(-1000,1000)


        if point[0] + x_offset > 5000 or point[0] + x_offset < -5000:   #ak by body sa mali vygenerovat za hranice tak otocim ich hodnotu
            x_offset = -x_offset
        elif point[1] + y_offset > 5000 or point[1] + y_offset < -5000:
            y_offset = -y_offset

        new_point = (point[0] + x_offset, point[1] + y_offset)

        points[new_point] = 0

    return points

# funkcia na zvolenie main_pointu ako centroidu, cize len nejaky fiktivny stred, ktory nieje realny bod
def centroids(clusters):
    for cluster in clusters:
        if len(cluster["points"]) == 0:
            continue
        x= 0
        y= 0
        for point in cluster["points"]:
            x += point[0]
            y += point[1]
        cluster["main_point"] = (int(x / len(cluster["points"])), int(int(y / len(cluster["points"]))))
        cluster["points"] = []
    return clusters

#podobne ako pri centroide, ale tu s medoidom kedy stred musi byt realny bod najblizsi stredu.
def monoids(clusters):
    for cluster in clusters:
        medoid_dist = float("inf")
        medoid = None
        for i in range(len(cluster["points"])):
            dist = 0
            for j in range(len(cluster["points"])):
                if i == j:
                    continue
                if dist > medoid_dist:
                    break
                dist += euc_dist(cluster["points"][i], cluster["points"][j])
            if medoid_dist is None or medoid_dist > dist:
                medoid = cluster["points"][i]
                medoid_dist = dist
        cluster["main_point"] = medoid
        cluster["points"] = []
    return clusters

#vseob. funkcia k_means, remember_all pri funkcii divisive nastavujem na false
def k_means(k, points, main_point, remember_all):
    global all_points
    clusters = []
    already_main_points = set()

    for i in range(k):
        centroid = random.choice(list(points.keys()))
        while centroid in already_main_points:
            centroid = random.choice(list(points.keys()))

        points[centroid] = i
        clusters.append({"main_point": centroid, "points": []})
        already_main_points.add(centroid)

    for point in points.keys():
        if point in already_main_points:
            continue

        for i in range(k):
            new_euclid_dist = euc_dist(point, clusters[i]["main_point"])
            old_euclid_dist = euc_dist(point, clusters[points[point]]["main_point"])
            if new_euclid_dist < old_euclid_dist:
                points[point] = i

        clusters[points[point]]["points"].append(point)

    if remember_all:
        all_points.append(copy.deepcopy(points))

    changed = True
    while changed:
        changed = False
        if main_point == "centroid":
            clusters = centroids(clusters)
        elif main_point == "medoid":
            clusters = monoids(clusters)
        for point in points.keys():
            for i in range(len(clusters)):
                new_euclid_dist = euc_dist(point, clusters[i]["main_point"])
                old_euclid_dist = euc_dist(point, clusters[points[point]]["main_point"])
                if new_euclid_dist < old_euclid_dist:
                    changed = True
                    points[point] = i
            clusters[points[point]]["points"].append(point)

        if remember_all:
            all_points.append(copy.deepcopy(points))

    if not remember_all:
        all_points.append(copy.deepcopy(points))

    return clusters

# divisivne, kedy sa pusta funkcia k_means pre k=2
def divisive(k, points):
    clusters = k_means(2, points, "centroid", False)

    while len(clusters) < k:

        averages = calculate_avg(clusters)
        cluster = clusters[averages.index(max(averages))]
        clusters.__delitem__(averages.index(max(averages)))

        if len(cluster["points"]) >= 2:
            new_points = {}

            for point in cluster["points"]:
                new_points[point] = 0

            temp_clusters = k_means(2, new_points, "centroid", False)
            clusters.append(temp_clusters[0])
            clusters.append(temp_clusters[1])

    return clusters

def main():

    global all_points, NUM_OF_POINTS
    clusters = []

    print("k-means with centroid -> 1\nk-means with medoid -> 2\ndivisive clustering -> 3")
    option = input("Which method: ")
    NUM_OF_POINTS = int(input("Number of points: "))
    k = int(input("k = "))

    points = generate_points()
    all_points.append(copy.deepcopy(points))
    start_time = time.time()

    if option == "1":
        clusters = k_means(k, points, "centroid", True)
        end_time = time.time()
        result(clusters)
        print("Time:", end_time - start_time, 's')

    elif option == "2":
        clusters = k_means(k, points, "medoid", True)
        end_time = time.time()
        result(clusters)
        print("Time:", end_time - start_time, 's')

    elif option == "3":
        clusters = divisive(k, points)
        end_time = time.time()
        result(clusters)
        print("Time:", end_time - start_time,'s')
    else:
        print("Wrong input")
        main()

    if option != "3":
        last_dict = all_points[-1]
        suradnice = list(last_dict)
        x_list = []
        y_list = []
        color = []

        for i in suradnice:
            x_list.append(i[0])
            y_list.append(i[1])


        for farba in suradnice:
            color.append(last_dict[farba[0],farba[1]])

        plt.scatter(x_list,y_list,c=color)

        plt.show()
    elif option == "3":
        x_list = []
        y_list = []
        farby = []
        counter = 0

        for a in clusters:
            for e in a["points"]:
                x_list.append(e[0])
                y_list.append(e[1])
                farby.append(counter)
            counter += 1
        plt.scatter(x_list, y_list, c=farby)

        plt.show()

    return 0

main()