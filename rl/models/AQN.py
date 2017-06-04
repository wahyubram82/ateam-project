import tensorflow as tf
from rl.models.DQN import DQN
from tensorflow.contrib import layers
import numpy as np


class AQN(DQN):
    def add_placeholders_op(self):
        """
        Adds placeholders to the graph

        These placeholders are used as inputs by the rest of the model building and will be fed
        data during training.  Note that when "None" is in a placeholder's shape, it's flexible
        (so we can use different batch sizes without rebuilding the model
        """

        ##############################################################
        """
        TODO: add placeholders:
              Remember that we stack 4 consecutive frames together, ending up with an input of shape
              (timesteps, 13, 4).
               - self.s: batch of states, type = float32
                         shape = (batch_size, audio timesteps, audio features, config.state_history)
               - self.a: batch of actions, type = int32
                         shape = (batch_size)
               - self.r: batch of rewards, type = float32
                         shape = (batch_size)
               - self.sp: batch of next states, type = float32
                         shape = (batch_size, audio timesteps, audio features, config.state_history)
               - self.done_mask: batch of done, type = bool
                         shape = (batch_size)
                         note that this placeholder contains bool = True only if we are done in 
                         the relevant transition
               - self.lr: learning rate, type = float32

        (Don't change the variable names!)

        HINT: variables from config are accessible with self.config.variable_name
              Also, you may want to use a dynamic dimension for the batch dimension.
              Check the use of None for tensorflow placeholders.

              you can also use the state_shape computed above.
        """
        ##############################################################
        ################YOUR CODE HERE (6-15 lines) ##################
        # TODO: Make sure we don't pass in the last 4 audio samples - only the current audio sample
        # ???: We changed this from uint8 to float32 - will this cause issues?
        s_shape = [None, None, self.config.num_mfcc]
        self.s = tf.placeholder(tf.float32, shape=s_shape, name='s')

        sl_shape = [None]
        self.sl = tf.placeholder(tf.int32, sl_shape, 'sl')

        a_shape = [None]
        self.a = tf.placeholder(tf.int32, shape=a_shape, name='a')

        r_shape = [None]
        self.r = tf.placeholder(tf.float32, shape=r_shape, name='r')

        # ???: We changed this from uint8 to float32 - will this cause issues?
        sp_shape = [None, None, self.config.num_mfcc]
        self.sp = tf.placeholder(tf.float32, shape=sp_shape, name='sp')

        slp_shape = [None]
        self.slp = tf.placeholder(tf.int32, slp_shape, 'slp')

        done_mask_shape = [None]
        self.done_mask = tf.placeholder(tf.bool, shape=done_mask_shape, name='done_mask')

        lr_shape = []
        self.lr = tf.placeholder(tf.float32, shape=lr_shape, name='lr')

        self.is_training = tf.placeholder(tf.bool, name='is_training')
        ##############################################################
        ######################## END YOUR CODE #######################

    def get_q_values_op(self, state, seq_len, is_training, scope, reuse=False):
        """
        Returns Q values for all actions

        Args:
            state: (tf tensor) 
                shape = (batch_size, img height, img width, nchannels)
            scope: (string) scope name, that specifies if target network or not
            reuse: (bool) reuse of variables in the scope

        Returns:
            out: (tf tensor) of shape = (batch_size, num_actions)
            :param seq_len: 
        """
        # this information might be useful
        num_actions = self.train_env.action_space.n
        ##############################################################
        """
        TODO: implement the computation of Q values like in the paper
                https://storage.googleapis.com/deepmind-data/assets/papers/DeepMindNature14236Paper.pdf
                https://www.cs.toronto.edu/~vmnih/docs/dqn.pdf

              you may find the section "model architecture" of the appendix of the 
              nature paper particulary useful.

              store your result in out of shape = (batch_size, num_actions)

        HINT: you may find tensorflow.contrib.layers useful (imported)
              make sure to understand the use of the scope param

              you can use any other methods from tensorflow
              you are not allowed to import extra packages (like keras,
              lasagne, cafe, etc.)

        """
        ##############################################################
        ################ YOUR CODE HERE - 10-15 lines ################
        ### YOUR CODE HERE (~10-15 lines)

        with tf.variable_scope(scope):
            # def rnn_dropout(_cell, output_keep_prob=None):
            #     return tf.contrib.rnn.DropoutWrapper(
            #         _cell,
            #         input_keep_prob=self.config.dropout_input_keep_prob,
            #         output_keep_prob=(output_keep_prob or
            #                           self.config.dropout_output_keep_prob),
            #         seed=self.config.random_seed
            #     )
            #
            # def rnn_input_dropout(_cell):
            #     return rnn_dropout(_cell, output_keep_prob=1.0)
            #
            # # For when we want to only apply dropout to the inputs
            # def dropout(_cell):
            #     return tf.nn.dropout(
            #         _cell,
            #         keep_prob=self.config.dropout_output_keep_prob,
            #         seed=self.config.random_seed
            #     )

            # Make rnn cells
            if self.config.rnn_cell_type == 'gru':
                # GRU
                rnn_cells = [
                    tf.contrib.rnn.GRUCell(self.config.n_hidden_rnn, reuse=reuse)
                    for _ in range(self.config.n_layers_rnn)
                ]
                # TODO: Just make seperate ops for train/val so we don't have
                #       to deal with this tf.cond BS that keeps erroring...
                # rnn_cells = [
                #     tf.cond(is_training,
                #             lambda: rnn_dropout(cell),
                #             lambda: cell)
                #     for cell in rnn_cells]
                state_is_tuple = False
            # else:
            #     # LSTM
            #     # Don't do recurrent dropout if val'ing/test'ing
            #     # TODO: Just make seperate ops for train/val so we don't have
            #     #       to deal with this tf.cond BS that keeps erroring...
            #     recurrent_keep_prob = tf.cond(is_training,
            #                                   lambda: tf.constant(self.config.recurrent_dropout_keep_prob),
            #                                   lambda: tf.constant(1.0))
            #
            #     # LSTMs with built-in layer-norm (like batch-norm) and recurrent-dropout (like dropout)
            #     rnn_cells = [
            #         tf.contrib.rnn.LayerNormBasicLSTMCell(
            #             self.config.n_hidden_rnn,
            #             dropout_keep_prob=recurrent_keep_prob,
            #             dropout_prob_seed=self.config.random_seed,
            #             reuse=reuse
            #         )
            #         for _ in range(self.config.n_layers_rnn)
            #     ]
            #     # TODO: Just make seperate ops for train/val so we don't have
            #     #       to deal with this tf.cond BS that keeps erroring...
            #     # # (only need to dropout the inputs b/c
            #     # # the LayerNormBasicLSTMCell dropsout the outputs)
            #     # rnn_cells = [tf.cond(is_training, lambda: rnn_input_dropout(cell), lambda: cell)
            #     #              for cell in rnn_cells]
            #     state_is_tuple = True

            rnn_stuff = tf.contrib.rnn.MultiRNNCell(rnn_cells, state_is_tuple=state_is_tuple)
            rnn_outputs, last_states = tf.nn.dynamic_rnn(rnn_stuff, state, sequence_length=seq_len, dtype=tf.float32)
            # if state_is_tuple:
            #     assert len(last_states) == self.config.n_layers_rnn
            #     last_states = tf.concat(last_states[0], axis=1)

            # Penultimate layer is a fully connected layer with batch-norm, activation,
            # and dropout
            if self.config.n_hidden_fc:
                fc = layers.fully_connected(
                    inputs=last_states,
                    num_outputs=self.config.n_hidden_fc,
                    activation_fn=tf.nn.relu,
                    reuse=reuse,
                    weights_initializer=layers.variance_scaling_initializer()
                )
                # fc = tf.contrib.layers.batch_norm(
                #     fc,
                #     center=True,
                #     scale=True,
                #     is_training=is_training,
                #     reuse=reuse
                # )
                # fc = tf.nn.elu(fc)
                # TODO: Just make seperate ops for train/val so we don't have
                #       to deal with this tf.cond BS that keeps erroring...
                # if self.config.dropout_output_keep_prob < 1.0 or self.config.dropout_input_keep_prob < 1.0:
                #     fc = tf.cond(is_training, lambda: dropout(fc), lambda: fc)
                logits_input = fc
            else:
                logits_input = last_states

            logits = layers.fully_connected(
                inputs=logits_input,
                num_outputs=num_actions,
                activation_fn=None,
                reuse=reuse,
                weights_initializer=layers.variance_scaling_initializer()
            )
        ##############################################################
        ######################## END YOUR CODE #######################
        return logits

    def build(self):
        """
        Build model by adding all necessary variables
        """
        # add placeholders
        self.add_placeholders_op()

        is_training = self.is_training

        # compute Q values of state
        s = self.s  # self.process_state(self.s)
        sl = self.sl
        self.q = self.get_q_values_op(s, sl, is_training, scope="q", reuse=False)

        # compute Q values of next state
        sp = self.sp  # self.process_state(self.sp)
        slp = self.slp
        self.target_q = self.get_q_values_op(sp, slp, is_training, scope="target_q", reuse=False)

        # add update operator for target network
        self.add_update_target_op("q", "target_q")

        # add square loss
        self.add_loss_op(self.q, self.target_q)

        # add optmizer for the main networks
        self.add_optimizer_op("q")

    def update_step(self, t, replay_buffer, lr):
        """
        Performs an update of parameters by sampling from replay_buffer

        Args:
            t: number of iteration (episode and move)
            replay_buffer: ReplayBuffer instance .sample() gives batches
            lr: (float) learning rate
        Returns:
            loss: (Q - Q_target)^2
        """
        s_batch, sl_batch, a_batch, r_batch, sp_batch, slp_batch, done_mask_batch = \
            replay_buffer.sample(self.config.batch_size)

        fd = {
            # inputs
            self.s: s_batch,
            self.sl: sl_batch,
            self.a: a_batch,
            self.r: r_batch,
            self.sp: sp_batch,
            self.slp: slp_batch,
            self.done_mask: done_mask_batch,
            self.lr: lr,
            self.is_training: True,
            # extra info
            self.avg_reward_placeholder: self.avg_reward,
            self.max_reward_placeholder: self.max_reward,
            self.std_reward_placeholder: self.std_reward,
            self.avg_q_placeholder: self.avg_q,
            self.max_q_placeholder: self.max_q,
            self.std_q_placeholder: self.std_q,
            self.eval_reward_placeholder: self.eval_reward,
        }

        loss_eval, grad_norm_eval, summary, _ = self.sess.run(
            [self.loss, self.grad_norm, self.merged, self.train_op], feed_dict=fd
        )

        # tensorboard stuff
        self.file_writer.add_summary(summary, t)

        return loss_eval, grad_norm_eval

    def get_best_action(self, state, is_training):
        """
        Return best action (used during testing/evaluation)

        Args:
            state: 4 consecutive observations from gym
            is_training: (bool) whether we're in the training phase
        Returns:
            action: (int)
            action_values: (np array) q values for all actions
        """
        # Feed in a batch of size 1 to get a single best action for this state
        seq_len = state.shape[0]
        feed_dict = {
            self.s: [state],
            self.sl: [seq_len],
            self.is_training: is_training
        }
        action_values = self.sess.run(self.q, feed_dict=feed_dict)[0]
        return np.argmax(action_values), action_values
