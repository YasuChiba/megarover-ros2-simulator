FROM nvidia/cuda:12.3.2-devel-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y sudo vim git wget unzip python-tk


# ロケールのセットアップ
RUN apt-get update && apt-get install -y locales && \
    dpkg-reconfigure locales && \
    locale-gen ja_JP ja_JP.UTF-8 && \
    update-locale LC_ALL=ja_JP.UTF-8 LANG=ja_JP.UTF-8
ENV LC_ALL   ja_JP.UTF-8
ENV LANG     ja_JP.UTF-8
ENV LANGUAGE ja_JP.UTF-8

# APTソースリストの設定
RUN apt-get update && apt-get install -y curl gnupg2 lsb-release
RUN curl https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | apt-key add - && \
    sh -c 'echo "deb [arch=amd64,arm64] http://packages.ros.org/ros2/ubuntu \
    `lsb_release -cs` main" > /etc/apt/sources.list.d/ros2-latest.list' && \
    apt-get update

# ROS2パッケージのインストール
RUN export ROS_DISTRO=humble && \
    apt update && \
    apt-get install -y ros-humble-desktop-full \
    python3-colcon-common-extensions python3-rosdep python3-argcomplete

#RUN apt-get install -y ros-humble-gazebo-* ros-humble-turtlebot3 ros-humble-turtlebot3-msgs
RUN apt update && \
    apt install -y ros-humble-navigation2 ros-humble-nav2-bringup ros-humble-ros-ign-gazebo ros-humble-ros-ign-bridge

ARG USERNAME=user
ARG GROUPNAME=user
ARG UID=1000
ARG GID=1000
ARG PASSWORD=user
RUN groupadd -g $GID $GROUPNAME && \
    useradd -m -s /bin/bash -u $UID -g $GID -G sudo $USERNAME && \
    echo $USERNAME:$PASSWORD | chpasswd && \
    echo "$USERNAME   ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
USER $USERNAME
RUN echo "source /opt/ros/humble/setup.bash" >> /home/$USERNAME/.bashrc
