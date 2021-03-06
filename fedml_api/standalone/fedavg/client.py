import logging

import torch
from torch import nn


class Client:

    def __init__(self, local_training_data, local_test_data, local_sample_number, args, device):
        self.local_training_data = local_training_data
        self.local_test_data = local_test_data
        self.local_sample_number = local_sample_number
        logging.info("self.local_sample_number = " + str(self.local_sample_number))

        self.args = args
        self.device = device

        self.criterion = nn.CrossEntropyLoss().to(device)

    def get_sample_number(self):
        return self.local_sample_number

    def train(self, net):
        net.train()
        # train and update
        # optimizer = torch.optim.SGD(net.parameters(), lr=self.args.lr, momentum=0.5)
        optimizer = torch.optim.Adam(filter(lambda p: p.requires_grad, net.parameters()), lr=self.args.lr,
                                          weight_decay=0.0001, amsgrad=True)

        epoch_loss = []
        for epoch in range(self.args.epochs):
            batch_loss = []
            for batch_idx, (images, labels) in enumerate(self.local_training_data):
                images, labels = images.to(self.device), labels.to(self.device)
                net.zero_grad()
                log_probs = net(images)
                loss = self.criterion(log_probs, labels)
                loss.backward()
                optimizer.step()
                logging.info('Update Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                    epoch, batch_idx * len(images), len(self.local_training_data.dataset),
                           100. * batch_idx / len(self.local_training_data), loss.item()))
                batch_loss.append(loss.item())
            epoch_loss.append(sum(batch_loss) / len(batch_loss))
        return net.cpu().state_dict(), sum(epoch_loss) / len(epoch_loss)

    def local_test(self, model_global, b_use_test_dataset=False):
        model_global.eval()
        model_global.to(self.device)
        test_loss = test_acc = test_total = 0.
        if b_use_test_dataset:
            test_data = self.local_test_data
        else:
            test_data = self.local_training_data
        with torch.no_grad():
            for batch_idx, (x, target) in enumerate(test_data):
                x = x.to(self.device)
                target = target.to(self.device)

                pred = model_global(x)
                loss = self.criterion(pred, target)
                _, predicted = torch.max(pred, 1)
                correct = predicted.eq(target).sum()

                test_acc += correct.item()
                test_loss += loss.item() * target.size(0)
                test_total += target.size(0)

        return test_acc, test_total, test_loss

    def global_test(self, model_global, global_test_data):
        model_global.eval()
        model_global.to(self.device)
        test_loss = test_acc = test_total = 0.
        with torch.no_grad():
            for batch_idx, (x, target) in enumerate(global_test_data):
                x = x.to(self.device)
                target = target.to(self.device)

                pred = model_global(x)
                loss = self.criterion(pred, target)
                _, predicted = torch.max(pred, 1)
                correct = predicted.eq(target).sum()

                test_acc += correct.item()
                test_loss += loss.item() * target.size(0)
                test_total += target.size(0)

        return test_acc, test_total, test_loss
