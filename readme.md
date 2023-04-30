

```
# Get's to the highway from state=22 in 500 steps
python -u main.py --init_state=s22
```


```
python -u main.py --checkpoint=output/20230430-175936_single_ant_plus_4_pixels/checkpoint_1000.pkl --exp_name=repro_single_ant_plus_4_pixels

python -u main.py --checkpoint=output/20230430-175936_single_ant_plus_4_pixels/checkpoint_1000.pkl --exp_name=repro_single_ant_plus_4_pixels --cells_to_remove_from_init_pkl=output/20230430-182205_repro_single_ant_plus_4_pixels/nonvisited_init_cells.pkl

python -u main.py --checkpoint=output/20230430-182757_repro_single_ant_plus_4_pixels_minus_nonvisited/checkpoint_1000.pkl --exp_name=repro_single_ant_plus_4_pixels_minus_nonvisited
```


```
python -u main.py --exp_name=single_ant

python -u main.py --checkpoint=output/20230430-183149_single_ant/checkpoint_9500.pkl --exp_name=repro_single_ant

python -u main.py --checkpoint=output/20230430-183149_single_ant/checkpoint_9500.pkl --exp_name=repro_repro_single_ant_minus_non_visited --cells_to_remove_from_init_pkl=output/20230430-183457_repro_single_ant/nonvisited_init_cells.pkl
```