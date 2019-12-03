
import torch
import torch.nn as nn
import torch.nn.functional as F


class Discriminator(nn.Module):
    def __init__(self, conv_dim):
        super(Discriminator, self).__init__()
        self.conv_dim = conv_dim
        self.layer1 = nn.Sequential(
            nn.Conv2d(3, conv_dim, kernel_size=3, stride=1, padding=1),
        )
        self.layer2 = nn.Sequential(
            nn.Conv2d(
                conv_dim, conv_dim, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(conv_dim),
        )
        self.layer3 = nn.Sequential(
            nn.Conv2d(
                conv_dim, conv_dim * 2, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(conv_dim * 2),
        )
        self.layer4 = nn.Sequential(
            nn.Conv2d(
                conv_dim * 2, conv_dim * 2, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(conv_dim * 2),
        )
        self.layer5 = nn.Sequential(
            nn.Conv2d(
                conv_dim * 2, conv_dim * 4, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(conv_dim * 4),
        )
        self.layer6 = nn.Sequential(
            nn.Conv2d(
                conv_dim * 4, conv_dim * 4, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(conv_dim * 4),
        )
        self.layer7 = nn.Sequential(
            nn.Conv2d(
                conv_dim * 4, conv_dim * 8, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(conv_dim * 8),
        )
        self.layer8 = nn.Sequential(
            nn.Conv2d(
                conv_dim * 8, conv_dim * 8, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(conv_dim * 8),
        )
        self.layer9 = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(
                conv_dim * 8, conv_dim * 16, kernel_size=1, stride=1, padding=0),
        )

        self.last = nn.Conv2d(conv_dim * 16, 1, kernel_size=1, stride=1, padding=0)

    def forward(self, x):
        print(self.conv_dim)
        out = F.relu(self.layer1(x))
        out = F.relu(self.layer2(out))
        out = F.relu(self.layer3(out))        
        out = F.relu(self.layer4(out))
        out = F.relu(self.layer5(out))
        out = F.relu(self.layer6(out))
        out = F.relu(self.layer7(out))
        out = F.relu(self.layer8(out))
        out = F.relu(self.layer9(out))
        out = self.last(out)
        print("oh myyyy", out.shape)
        out = torch.sigmoid(out.view(x.shape[0]))
        return out


class Generator(nn.Module):
    def __init__(self, conv_dim, scale_factor):
        super(Generator, self).__init__()
        self.scale_factor = scale_factor

        self.layer1 = nn.Conv2d(
            3, conv_dim, kernel_size=9, stride=1, padding=4)

        self.residual_layers = nn.Sequential(
            ResidualBlock(conv_dim),
            ResidualBlock(conv_dim),
            ResidualBlock(conv_dim),
            ResidualBlock(conv_dim),
            ResidualBlock(conv_dim),
        )

        self.layer2 = nn.Sequential(
            nn.Conv2d(conv_dim, conv_dim, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(conv_dim)
        )

        upsample_layers = []
        for _ in range(self.scale_factor // 2):
            print("hi", conv_dim)
            upsample_layers.append(UpsampleBLock(conv_dim))
        
        self.upsample_layers = nn.Sequential(
            *upsample_layers
        )

        self.layer3 = nn.Conv2d(
            conv_dim, 3, kernel_size=9, stride=1, padding=4)
    
    def forward(self, x):
        print("x", x.shape, x.type(), self.layer1(x).type())
        orig_out = F.relu(self.layer1(x))
        out = self.residual_layers(orig_out)
        out = self.layer2(out + orig_out)
        print("holaaa", out.shape, orig_out.shape)
        out = self.upsample_layers(out)
        print("anoda one", out.shape, orig_out.shape)
        out = self.layer3(out)
        return out


class ResidualBlock(nn.Module):
    def __init__(self, conv_dim):
        super(ResidualBlock, self).__init__()

        self.layer1 = nn.Sequential(
            nn.Conv2d(conv_dim, conv_dim, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(conv_dim)
        )
        self.layer2 = nn.Sequential(
            nn.Conv2d(conv_dim, conv_dim, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(conv_dim)
        )

    def forward(self, x):
        out = F.relu(self.layer1(x))
        out = self.layer2(out)

        return out + x


class UpsampleBLock(nn.Module):
    def __init__(self, conv_dim):
        print("hooola", conv_dim)
        super(UpsampleBLock, self).__init__()
        self.layer = nn.Sequential(
            nn.Conv2d(conv_dim, conv_dim * 4,
                                kernel_size=3, stride=1, padding=1),
            nn.PixelShuffle(2)
        )

    def forward(self, x):
        print("x", x.shape)
        out = F.relu(self.layer(x))
        return out


