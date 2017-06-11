import framestream
import matplotlib.pyplot as plt
import multibag
import numpy as np
import os
import pickle

FIG_DIR = 'figs'

def make_and_save_histograms(bag, poses, dims, show = False):
    bins = 50
    poses = np.stack(poses)
    print(poses.shape)
    histograms = []

    f, axarr = plt.subplots(len(dims))
    plt.title(bag)

    for pose_dim in dims:
        pose_slice = poses[:, pose_dim]
        hist = np.histogram(pose_slice, bins=bins)
        histograms.append(hist)

        sub = axarr[pose_dim]
        sub.set_title(pose_dim)
        sub.hist(pose_slice, bins=100)

    filename = 'posehist' + bag.replace('/', '_') + '.png'
    filename = os.path.join(FIG_DIR, filename)
    f.set_size_inches(16, 10)
    f.savefig(filename, bbox_inches='tight', dpi=200)
    if show:
        plt.show()
    plt.close()

    histograms = np.stack(histograms)
    return histograms

class PoseHistograms:
    def __init__(self, histograms_by_bag, histograms_all):
        self.histograms_by_bag = histograms_by_bag
        self.histograms_all = histograms_all

def make_histograms(bag_tracklets, show):
    histograms_by_bag = dict()
    all_poses = []

    # bag_tracklets = [multibag.BagTracklet('/data/Didi-Release-2/Data/1/3.bag', '/data/output/tracklet/1/3/tracklet_labels.xml')]

    dims = [i for i in range(6)]
    print('dims', dims)

    for bt in bag_tracklets:
        print(bt.bag)
        poses = []

        msgstream = framestream.FrameStream()
        msgstream.start_read(bt.bag, bt.tracklet)
        while not msgstream.empty():
            sample = msgstream.next()
            poses.append(sample.pose)

        histograms_by_bag[bt.bag] = make_and_save_histograms(bt.bag, poses, dims, show)

        all_poses += poses

        print('len(poses)', len(poses))
        print('len(all_poses)', len(all_poses))

    all_poses = np.stack(all_poses)
    print('all_poses.shape', all_poses.shape)

    histograms_all = make_and_save_histograms('all_bags', all_poses, dims, show)

    pose_histograms = PoseHistograms(histograms_by_bag, histograms_all)

    with open(os.path.join(FIG_DIR, 'posehist.p'), 'wb') as f:
        pickle.dump(pose_histograms, f)

if __name__ == '__main__':
    if not os.path.exists(FIG_DIR):
        os.makedirs(FIG_DIR)

    bt = multibag.find_bag_tracklets('/data/Didi-Release-2/Data/', '/data/output/tracklet/')

    make_histograms(bt, show = False)