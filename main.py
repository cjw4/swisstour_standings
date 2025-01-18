from dbinteract import populate_db_by_event, add_sda_info, calculate_swisstour_pts, create_standings
import time

def main():
    # time the execution
    start_time = time.time()

    # define the event order and points for standings table
    event_order_and_pts = {76703:100,  # Meggen
                            75982:200,  # Chili Open
                            79574:200,  # Revolution
                            79619:100,  # Spring Clang MPO/FPO
                            79567:100,  # Spring Clang Other
                            81268:100,  # GPO
                            81952:100,  # Birdie Fest
                            80000:200,  # ZDGO
                            83268:200,  # Eagle Open
                            83724:100,  # Lila´s
                            83214:100,  # Winterthur
                            84636:100,  # Lakeside
                            82431:250}  # Bern Open
    
    populate_db_by_event(76703)                   # Meggen
    populate_db_by_event(75982)                   # Chili Open
    populate_db_by_event(79574)                   # Revolution
    populate_db_by_event(79619)                   # Spring Clang MPO/FPO
    populate_db_by_event(79567)                   # Spring Clang Other
    populate_db_by_event(81268)                   # GPO
    populate_db_by_event(81952)                   # Birdie Fest
    populate_db_by_event(80000)                   # ZDGO
    populate_db_by_event(83268)                   # Eagle Open
    populate_db_by_event(83724)                   # Lila´s
    populate_db_by_event(83214)                   # Winterthur
    populate_db_by_event(84636)                   # Lakeside
    populate_db_by_event(82431)                   # Bern Open

    add_sda_info()

    calculate_swisstour_pts(event_order_and_pts)

    create_standings(event_order_and_pts)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")

if __name__ == '__main__':
    main()